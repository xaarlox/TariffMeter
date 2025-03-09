create database electricity_db;

use electricity_db;

create table  tariffs(
	tariff_id int primary key auto_increment,
    day_rate decimal(5, 2) not null,
    night_rate decimal(5, 2) not null,
    day_adjustment int default 100,
    night_adjustment int default 80
);

create table meters(
	meter_id varchar(20) primary key,
    last_date date not null,
    prev_day_kwh int not null,
    prev_night_kwh int not null
);

create table history_table(
	history_id int primary key auto_increment,
    meter_id varchar(20),
    curr_date date not null,
    day_kwh int not null,
    night_kwh int not null,
    total_cost decimal(7, 2) not null,
    constraint fk_history_meter foreign key (meter_id) references meters(meter_id)
);

insert into tariffs(day_rate, night_rate) values(4.32, 2.16);