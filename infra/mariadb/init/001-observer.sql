-- The product comparison account can inspect server/session variables but has no
-- privileges on ATLAS or lab tables. Lab mutations use the separate atlas_lab user.
CREATE USER IF NOT EXISTS 'atlas_observer'@'%' IDENTIFIED BY 'atlas_observer_dev_only';
GRANT USAGE ON *.* TO 'atlas_observer'@'%';
