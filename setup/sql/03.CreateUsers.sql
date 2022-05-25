CREATE USER OR REPLACE app_pdc IDENTIFIED WITH plaintext_password BY 'nopass' HOST ANY

GRANT ALL ON rt_dev.* TO app_pdc

CREATE USER OR REPLACE app_pdc_prod IDENTIFIED WITH plaintext_password BY 'nopass' HOST LOCAL

GRANT ALL ON rt.* TO app_pdc_prod