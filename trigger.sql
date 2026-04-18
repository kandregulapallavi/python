set serveroutput on
create or replace trigger change_date
before insert on admission
for each row
begin
	:New admission_date:SYSDATE:
end change_date;
/