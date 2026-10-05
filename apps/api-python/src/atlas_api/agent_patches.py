"""Human-approved, local-only repository patch gateway.

This module is intentionally smaller than a general patch engine. A proposal may
replace one bounded line range in one existing allowlisted text file. The server
derives both the diff and the approval digest from trusted repository bytes; callers
cannot upload an opaque patch and ask ATLAS to apply it blindly.
"""

from __future__ import annotations

import ast
import difflib
import hashlib
import json
import os
import stat
import tempfile
import threading
from datetime import datetime
from pathlib import Path, PurePosixPath
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from atlas_api.config import Settings
from atlas_api.models import AIRepositoryPatchProposal

_WRITE_LOCK = threading.Lock()
_ALLOWED_PREFIXES = {
    "apps",
    "content",
    "datasets",
    "docs",
    "labs",
    "packages",
    "registry",
    "scripts",
    "security",
    "work",
}
_ALLOWED_SUFFIXES = {".css", ".json", ".md", ".py", ".ts", ".tsx", ".yaml", ".yml"}
_DENIED_NAMES = {
    ".env",
    ".gitignore",
    "package-lock.json",
    "pnpm-lock.yaml",
    "yarn.lock",
}


class PatchPolicyError(RuntimeError):
    """A proposal or filesystem state violated the reviewed patch policy."""


class PatchConflictError(PatchPolicyError):
    """Repository bytes changed after the proposal was reviewed."""


class PatchProposalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    path: str = Field(min_length=1, max_length=240)
    expected_sha256: str = Field(pattern=r"^[0-9a-f]{64}$")
    start_line: int = Field(ge=1)
    end_line: int = Field(ge=1)
    replacement: str = Field(max_length=100_000)
    summary: str = Field(min_length=5, max_length=200)
    rationale: str = Field(min_length=10, max_length=2_000)

    @model_validator(mode="after")
    def ordered_range(self) -> PatchProposalCreate:
        if self.end_line < self.start_line:
            raise ValueError("end_line must be at or after start_line")
        return self


class PatchApproval(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    proposal_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirmation: Literal["APPLY EXACT PATCH"]


class PatchRollback(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    proposal_digest: str = Field(pattern=r"^[0-9a-f]{64}$")
    confirmation: Literal["ROLL BACK EXACT PATCH"]


class PatchProposalRead(BaseModel):
    """Review DTO intentionally omits captured full source contents."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    path: str
    summary: str
    rationale: str
    status: str
    original_sha256: str
    patched_sha256: str
    proposal_digest: str
    unified_diff: str
    start_line: int
    end_line: int
    proposed_by: str
    approved_by: str | None
    failure_reason: str | None
    created_at: datetime
    approved_at: datetime | None
    applied_at: datetime | None
    rolled_back_at: datetime | None


class PatchGateway:
    """Resolve, validate, apply, and roll back exact repository byte transitions."""

    def __init__(self, settings: Settings) -> None:
        self.root = Path(settings.repository_root).resolve()
        self.max_file_bytes = settings.ai_patch_max_file_bytes
        self.max_changed_lines = settings.ai_patch_max_changed_lines

    def _resolve(self, raw_path: str) -> Path:
        path = PurePosixPath(raw_path)
        if path.is_absolute() or not path.parts or any(
            part in {"", ".", ".."} or part.startswith(".") for part in path.parts
        ):
            raise PatchPolicyError("path is outside the patch allowlist")
        if path.parts[0] not in _ALLOWED_PREFIXES:
            raise PatchPolicyError("path prefix is not patchable")
        if path.name in _DENIED_NAMES or path.suffix.lower() not in _ALLOWED_SUFFIXES:
            raise PatchPolicyError("file type is not patchable")

        unresolved = self.root.joinpath(*path.parts)
        cursor = self.root
        for part in path.parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise PatchPolicyError("symbolic links are not patchable")
        try:
            candidate = unresolved.resolve(strict=True)
            candidate.relative_to(self.root)
        except (FileNotFoundError, ValueError) as error:
            raise PatchPolicyError("patch target must be an existing repository file") from error
        if not candidate.is_file():
            raise PatchPolicyError("patch target must be a regular file")
        return candidate

    @staticmethod
    def _sha(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()

    def _read(self, path: Path) -> str:
        data = path.read_bytes()
        if len(data) > self.max_file_bytes:
            raise PatchPolicyError("patch target exceeds the configured file limit")
        if b"\x00" in data:
            raise PatchPolicyError("binary files are not patchable")
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError as error:
            raise PatchPolicyError("patch target must be UTF-8 text") from error

    @staticmethod
    def _validate_content(path: Path, content: str) -> None:
        if "\x00" in content:
            raise PatchPolicyError("replacement contains a NUL byte")
        try:
            if path.suffix.lower() == ".py":
                ast.parse(content, filename=path.name)
            elif path.suffix.lower() == ".json":
                json.loads(content)
        except (SyntaxError, json.JSONDecodeError) as error:
            raise PatchPolicyError(
                f"replacement does not produce valid {path.suffix} syntax"
            ) from error

    def build(
        self, data: PatchProposalCreate, *, organization_id: UUID, actor: str
    ) -> AIRepositoryPatchProposal:
        path = self._resolve(data.path)
        original = self._read(path)
        if self._sha(original) != data.expected_sha256:
            raise PatchConflictError("source hash no longer matches the reviewed file")
        original_lines = original.splitlines(keepends=True)
        if data.end_line > len(original_lines):
            raise PatchPolicyError("replacement range exceeds the current file")
        removed = data.end_line - data.start_line + 1
        replacement_lines = data.replacement.splitlines(keepends=True)
        if data.replacement and not data.replacement.endswith(("\n", "\r")):
            # Preserve line semantics for a range replacement that is not at EOF.
            if data.end_line < len(original_lines):
                replacement_lines[-1] += "\n"
        if max(removed, len(replacement_lines)) > self.max_changed_lines:
            raise PatchPolicyError("proposal exceeds the configured changed-line limit")
        patched_lines = (
            original_lines[: data.start_line - 1]
            + replacement_lines
            + original_lines[data.end_line :]
        )
        patched = "".join(patched_lines)
        if patched == original:
            raise PatchPolicyError("proposal does not change the file")
        if len(patched.encode("utf-8")) > self.max_file_bytes:
            raise PatchPolicyError("patched file exceeds the configured file limit")
        self._validate_content(path, patched)
        diff = "".join(
            difflib.unified_diff(
                original.splitlines(keepends=True),
                patched.splitlines(keepends=True),
                fromfile=f"a/{data.path}",
                tofile=f"b/{data.path}",
                n=3,
            )
        )
        if len(diff.encode("utf-8")) > 128_000:
            raise PatchPolicyError("generated diff exceeds the review limit")
        original_sha = self._sha(original)
        patched_sha = self._sha(patched)
        digest_payload = json.dumps(
            {
                "path": data.path,
                "original_sha256": original_sha,
                "patched_sha256": patched_sha,
                "start_line": data.start_line,
                "end_line": data.end_line,
                "summary": data.summary,
                "rationale": data.rationale,
            },
            sort_keys=True,
            separators=(",", ":"),
        )
        digest = hashlib.sha256(digest_payload.encode("utf-8")).hexdigest()
        return AIRepositoryPatchProposal(
            organization_id=organization_id,
            path=data.path,
            summary=data.summary,
            rationale=data.rationale,
            original_sha256=original_sha,
            patched_sha256=patched_sha,
            proposal_digest=digest,
            original_content=original,
            patched_content=patched,
            unified_diff=diff,
            start_line=data.start_line,
            end_line=data.end_line,
            proposed_by=actor,
        )

    def _atomic_replace(self, path: Path, content: str) -> None:
        mode = stat.S_IMODE(path.stat().st_mode)
        temporary_name = ""
        try:
            with tempfile.NamedTemporaryFile(
                mode="wb", prefix=".atlas-patch-", dir=path.parent, delete=False
            ) as temporary:
                temporary_name = temporary.name
                temporary.write(content.encode("utf-8"))
                temporary.flush()
                os.fsync(temporary.fileno())
            os.chmod(temporary_name, mode)
            os.replace(temporary_name, path)
        finally:
            if temporary_name and os.path.exists(temporary_name):
                os.unlink(temporary_name)

    def apply(self, proposal: AIRepositoryPatchProposal) -> None:
        with _WRITE_LOCK:
            path = self._resolve(proposal.path)
            current = self._read(path)
            if self._sha(current) != proposal.original_sha256:
                raise PatchConflictError("source changed after proposal review")
            if self._sha(proposal.patched_content) != proposal.patched_sha256:
                raise PatchPolicyError("stored patched content failed integrity verification")
            self._validate_content(path, proposal.patched_content)
            self._atomic_replace(path, proposal.patched_content)
            if self._sha(self._read(path)) != proposal.patched_sha256:
                raise PatchPolicyError("post-write verification failed")

    def rollback(self, proposal: AIRepositoryPatchProposal) -> None:
        with _WRITE_LOCK:
            path = self._resolve(proposal.path)
            current = self._read(path)
            if self._sha(current) != proposal.patched_sha256:
                raise PatchConflictError("patched file changed after application")
            if self._sha(proposal.original_content) != proposal.original_sha256:
                raise PatchPolicyError("stored rollback content failed integrity verification")
            self._validate_content(path, proposal.original_content)
            self._atomic_replace(path, proposal.original_content)
            if self._sha(self._read(path)) != proposal.original_sha256:
                raise PatchPolicyError("post-rollback verification failed")
