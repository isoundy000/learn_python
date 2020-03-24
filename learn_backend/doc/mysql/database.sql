SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ----------------------------
-- Table structure for paylog_0
-- ----------------------------
DROP TABLE IF EXISTS `paylog_0`;
CREATE TABLE `paylog_0`
(
    order_id varchar(255) NOT NULL,
    admin varchar(32),
    gift_coin mediumint,
    level smallint,
    old_coin mediumint,
    order_coin mediumint,
    order_money smallint,
    order_time varchar(255),
    platform varchar(32),
    product_id mediumint,
    raw_data blob,
    reason blob,
    scheme_id varchar(255),
    user_id varchar(32),
    uin varchar(32),
    PRIMARY KEY(order_id),
    index(order_id),
    index(order_time),
    index(user_id)
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Compact;


-- ----------------------------
-- Table structure for paylog_0
-- ----------------------------
DROP TABLE IF EXISTS `paylog_1`;
CREATE TABLE `paylog_0`
(
    order_id varchar(255) NOT NULL,
    admin varchar(32),
    gift_coin mediumint,
    level smallint,
    old_coin mediumint,
    order_coin mediumint,
    order_money smallint,
    order_time varchar(255),
    platform varchar(32),
    product_id mediumint,
    raw_data blob,
    reason blob,
    scheme_id varchar(255),
    user_id varchar(32),
    uin varchar(32),
    PRIMARY KEY(order_id),
    index(order_id),
    index(order_time),
    index(user_id)
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Compact;

-- ----------------------------
-- Table structure for spendlog_0
-- ----------------------------
DROP TABLE IF EXISTS `spendlog_0`;
CREATE TABLE `spendlog_0`
(
    order_id int(50) NOT NULL auto_increment,
    uid varchar(32),
    level int(4),
    subtime varchar(32),
    coin_num int(10),
    coin_1st int(10),
    coin_2nd int(10),
    goods_type varchar(50),
    goods_subtype varchar(50),
    goods_name varchar(100),
    goods_num int(10),
    goods_price int(10),
    goods_cnname varchar(100),
    args varchar(500),
    PRIMARY KEY(order_id),
    index(subtime),
    index(uid)
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Compact;


-- ----------------------------
-- Table structure for spendlog_1
-- ----------------------------
DROP TABLE IF EXISTS `spendlog_1`;
CREATE TABLE `spendlog_0`
(
    order_id int(50) NOT NULL auto_increment,
    uid varchar(32),
    level int(4),
    subtime varchar(32),
    coin_num int(10),
    coin_1st int(10),
    coin_2nd int(10),
    goods_type varchar(50),
    goods_subtype varchar(50),
    goods_name varchar(100),
    goods_num int(10),
    goods_price int(10),
    goods_cnname varchar(100),
    args varchar(500),
    PRIMARY KEY(order_id),
    index(subtime),
    index(uid)
) ENGINE = InnoDB
  CHARACTER SET = utf8mb4
  COLLATE = utf8mb4_general_ci
  ROW_FORMAT = Compact;