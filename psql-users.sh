psql -U postgres -c "create user test with superuser password 'test';" # pragma: allowlist secret
psql -U postgres -c "create database automated_test with owner test;"