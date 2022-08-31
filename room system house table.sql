create table house (
    houseID int NOT NULL AUTO_INCREMENT,
    city char(6) NOT NULL,
    area char(6) NOT NULL,
    houseaddress char(20) NOT NULL,
	lease bool default false,
    leasebegins date,
    leaseends date,
    rent int NOT NULL,
    deposit int,
    discount int default 0,
    registrantID char(16) NOT NULL,
    IMG1 LONGBLOB,
    IMG2 LONGBLOB,
    IMG3 LONGBLOB,
	createtime timestamp default current_timestamp,
    updatetime timestamp on update current_timestamp,
    PRIMARY KEY(houseID)
	)engine=InnoDB charset=utf8mb4 collate=utf8mb4_unicode_ci;