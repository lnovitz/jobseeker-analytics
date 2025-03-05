DO
$do$
BEGIN
   IF NOT EXISTS (
      SELECT 1
      FROM   pg_database
      WHERE  datname = 'jobseeker_analytics'
      ) THEN
      EXECUTE 'CREATE DATABASE jobseeker_analytics';
   END IF;
END
$do$;
