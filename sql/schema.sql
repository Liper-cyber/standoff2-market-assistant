-- =========================================================
-- Standoff Trade — инициализация базы данных
-- Версия PostgreSQL: 18.x
-- Создаёт структуру + заливает скины и один аккаунт
-- =========================================================

-- Настройки сессии для воспроизводимости
SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

BEGIN;

-- ---------------------------------------------------------
-- 1. Структура таблиц
-- ---------------------------------------------------------

CREATE TABLE IF NOT EXISTS public.nox_devices
(
    id          serial NOT NULL,
    id_nox      integer NOT NULL,
    create_at   timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status      character varying(20) DEFAULT 'не запущен'::character varying,
    proxy_port  integer,
    CONSTRAINT nox_devices_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.account
(
    id              serial NOT NULL,
    nox_devices_id  integer NOT NULL,
    gold            integer DEFAULT 0,
    name            character varying(50),
    gmail           character varying(50) NOT NULL,
    user_id         integer NOT NULL,
    create_at       timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT account_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.skins
(
    id                 serial NOT NULL,
    name               character varying(100) NOT NULL,
    rarity             character varying(100) NOT NULL,
    url                character varying(255) NOT NULL,
    interval_minutes   integer DEFAULT 10,
    sell_price         numeric(10, 2),
    max_buy            numeric(10, 2) DEFAULT 0.05,
    min_buy            numeric(10, 2) DEFAULT 0.03,
    buy_price          numeric(10, 2) DEFAULT NULL,
    sell_global_price  numeric(10, 2),
    CONSTRAINT skins_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.account_skins
(
    account_id     integer,
    skin_id        integer,
    last_buy       timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    count          integer DEFAULT 0,
    last_sell      timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    sell_count     integer DEFAULT 0,
    wait_attempts  integer DEFAULT 0,
    fast_order     integer DEFAULT 0,
    is_sale        boolean DEFAULT true,
    is_buy         boolean DEFAULT true
);

CREATE TABLE IF NOT EXISTS public.history_account
(
    id           serial NOT NULL,
    id_account   integer,
    history_json text,
    created_at   timestamp without time zone DEFAULT now(),
    CONSTRAINT history_account_pkey PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS public.expenses
(
    id           serial NOT NULL,
    category     character varying(100) NOT NULL,
    amount       numeric(10, 2) NOT NULL,
    description  text,
    date         date DEFAULT CURRENT_DATE,
    CONSTRAINT expenses_pkey PRIMARY KEY (id)
);

-- ---------------------------------------------------------
-- 2. Внешние ключи и индексы
-- ---------------------------------------------------------

ALTER TABLE IF EXISTS public.account
    ADD CONSTRAINT fk_account_nox_devices FOREIGN KEY (nox_devices_id)
    REFERENCES public.nox_devices (id)
    ON UPDATE CASCADE
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.account_skins
    ADD CONSTRAINT fk_account_skins_account FOREIGN KEY (account_id)
    REFERENCES public.account (id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE IF EXISTS public.account_skins
    ADD CONSTRAINT fk_account_skins_skin FOREIGN KEY (skin_id)
    REFERENCES public.skins (id)
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

CREATE INDEX IF NOT EXISTS idx_account_skins_skin_id
    ON public.account_skins(skin_id);

ALTER TABLE IF EXISTS public.history_account
    ADD CONSTRAINT history_account_id_account_fkey FOREIGN KEY (id_account)
    REFERENCES public.account (id)
    ON UPDATE NO ACTION
    ON DELETE CASCADE;

-- ---------------------------------------------------------
-- 3. Данные: устройство, аккаунт, скины
-- ---------------------------------------------------------

-- Эмулятор (нужен, чтобы account.nox_devices_id ссылался на существующую строку)
INSERT INTO public.nox_devices (id_nox)
    VALUES (0);

-- Скины
INSERT INTO public.skins (id, name, rarity, url, interval_minutes, sell_price, max_buy, min_buy, buy_price, sell_global_price) VALUES
    (10, 'Powergame',    'uncommon', 'M4(Powergame)',       25, 0.40, 0.32, 0.31, 0.31, 1.45),
    (12, 'Vesper Haze',  'uncommon', 'SPAS(VesperHaze)',    20, 0.28, 0.19, 0.16, 0.18, 0.54),
    ( 9, 'Stainless',    'rare',     'M4A1(Stainless)',     15, 0.51, 0.38, 0.36, 0.36, 2.79),
    ( 5, 'Acid Carbon',  'common',   'FNFAL(AcidCarbon)',    5, 0.09, 0.07, 0.06, 0.06, 0.17),
    ( 3, 'Blaster',      'common',   'SM1014(Blaster)',      5, 0.09, 0.07, 0.06, 0.06, 0.17),
    ( 6, 'Thorn',        'common',   'MP7(Thorn)',          10, 0.10, 0.11, 0.09, 0.09, 0.26),
    ( 7, 'Aurora',       'uncommon', 'TEC9(Aurora)',        15, 0.17, 0.14, 0.13, 0.13, 0.30),
    ( 4, 'Jungle',       'common',   'P90(Jungle)',          5, 0.09, 0.08, 0.07, 0.07, 0.19),
    (13, 'Impale',       'common',   'M40(Impale)',         15, 0.18, 0.14, 0.13, 0.13, 0.26),
    (14, 'Precision',    'common',   'MP7(Precision)',      10, 0.14, 0.12, 0.11, 0.11, 0.29),
    (15, 'Red-Hot',      'common',   'FNFAL(Red-Hot)',      10, 0.14, 0.12, 0.11, 0.11, 0.27),
    (11, 'Fiend',        'uncommon', 'USP(Fiend)',          20, 0.23, 0.19, 0.17, 0.17, 0.49),
    (16, 'Tech Shard',   'common',   'M110(TechShard)',     10, 0.13, 0.11, 0.10, 0.11, 0.27),
    ( 8, 'Worm',         'uncommon', 'AKR(Worm)',           30, 0.55, 0.36, 0.35, 0.35, 1.12),
    (17, 'Vector',       'uncommon', 'MP5(Vector)',         15, 0.26, 0.21, 0.20, 0.20, 0.78),
    ( 1, 'Pixel V2',     'uncommon', 'UMP45(Pixel V2)',     20, 0.15, 0.14, 0.12, 0.12, 0.32);

-- Синхронизация автоинкремента skins.id
SELECT pg_catalog.setval('public.skins_id_seq', 17, true);


-- Аккаунт (замените gmail и user_id на свои)
INSERT INTO public.account (nox_devices_id, gmail, user_id)
    VALUES (0, 'your@gmail.com', 45215222);

COMMIT;