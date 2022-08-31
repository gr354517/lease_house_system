create table registrant (
	registrantID char(18) NOT NULL,
    Name char(18) NOT NULL,
    email char(30) NOT NULL,
    phone_number char(10) NOT NULL,
    PRIMARY KEY(registrantID)
    )engine=InnoDB charset=utf8mb4 collate=utf8mb4_unicode_ci;