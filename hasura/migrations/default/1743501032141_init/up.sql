SET check_function_bodies = false;
CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;
COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';
CREATE TABLE public.boat_betting_contribute_rate_aggregations (
    stadium_tel_code integer NOT NULL,
    boat_number integer NOT NULL,
    aggregated_on date NOT NULL,
    quinella_rate double precision NOT NULL,
    trio_rate double precision,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.boat_settings (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    pit_number integer NOT NULL,
    boat_number integer,
    motor_number integer,
    tilt double precision,
    is_propeller_renewed boolean,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.circumference_exhibition_records (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    pit_number integer NOT NULL,
    exhibition_time double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.disqualified_race_entries (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    pit_number integer NOT NULL,
    disqualification integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.events (
    stadium_tel_code integer NOT NULL,
    starts_on date NOT NULL,
    title character varying(255) NOT NULL,
    grade integer NOT NULL,
    kind integer NOT NULL,
    is_canceled boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.motor_betting_contribute_rate_aggregations (
    stadium_tel_code integer NOT NULL,
    motor_number integer NOT NULL,
    aggregated_on date NOT NULL,
    quinella_rate double precision NOT NULL,
    trio_rate double precision,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.motor_maintenances (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    motor_number integer NOT NULL,
    exchanged_parts integer NOT NULL,
    quantity integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.motor_renewals (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.odds (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    betting_method integer NOT NULL,
    betting_number integer NOT NULL,
    ratio double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.payoffs (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    betting_method integer NOT NULL,
    betting_number integer NOT NULL,
    amount integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.race_entries (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    racer_registration_number integer NOT NULL,
    pit_number integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.race_records (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    pit_number integer NOT NULL,
    course_number integer NOT NULL,
    start_time double precision,
    race_time double precision,
    arrival integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.racer_conditions (
    racer_registration_number integer NOT NULL,
    date date NOT NULL,
    weight double precision NOT NULL,
    adjust double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.racer_winning_rate_aggregations (
    racer_registration_number integer NOT NULL,
    aggregated_on date NOT NULL,
    rate_in_all_stadium double precision NOT NULL,
    rate_in_event_going_stadium double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.racers (
    registration_number integer NOT NULL,
    last_name character varying(255) DEFAULT ''::character varying NOT NULL,
    first_name character varying(255) DEFAULT ''::character varying NOT NULL,
    gender integer,
    term integer,
    birth_date date,
    branch_id integer,
    birth_prefecture_id integer,
    height integer,
    status integer,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE SEQUENCE public.racers_registration_number_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.racers_registration_number_seq OWNED BY public.racers.registration_number;
CREATE TABLE public.races (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    title character varying(255),
    is_course_fixed boolean NOT NULL,
    is_stabilizer_used boolean NOT NULL,
    number_of_laps integer NOT NULL,
    betting_deadline_at timestamp without time zone,
    is_canceled boolean DEFAULT false NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.stadiums (
    tel_code integer NOT NULL,
    name character varying(255) NOT NULL,
    prefecture_id integer NOT NULL,
    water_quality integer NOT NULL,
    has_tide_fluctuation boolean NOT NULL,
    lat double precision NOT NULL,
    lng double precision NOT NULL,
    elevation double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE SEQUENCE public.stadiums_tel_code_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
ALTER SEQUENCE public.stadiums_tel_code_seq OWNED BY public.stadiums.tel_code;
CREATE TABLE public.start_exhibition_records (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    pit_number integer NOT NULL,
    course_number integer NOT NULL,
    start_time double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.weather_conditions (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    is_in_performance boolean NOT NULL,
    weather integer NOT NULL,
    wind_velocity double precision NOT NULL,
    wind_angle double precision,
    wavelength double precision,
    air_temperature double precision NOT NULL,
    water_temperature double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
CREATE TABLE public.winning_race_entries (
    stadium_tel_code integer NOT NULL,
    date date NOT NULL,
    race_number integer NOT NULL,
    pit_number integer NOT NULL,
    winning_trick integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);
ALTER TABLE ONLY public.racers ALTER COLUMN registration_number SET DEFAULT nextval('public.racers_registration_number_seq'::regclass);
ALTER TABLE ONLY public.stadiums ALTER COLUMN tel_code SET DEFAULT nextval('public.stadiums_tel_code_seq'::regclass);
ALTER TABLE ONLY public.boat_betting_contribute_rate_aggregations
    ADD CONSTRAINT boat_betting_contribute_rate_aggregations_pkey PRIMARY KEY (stadium_tel_code, boat_number, aggregated_on);
ALTER TABLE ONLY public.boat_settings
    ADD CONSTRAINT boat_settings_pkey PRIMARY KEY (stadium_tel_code, date, race_number, pit_number);
ALTER TABLE ONLY public.circumference_exhibition_records
    ADD CONSTRAINT circumference_exhibition_records_pkey PRIMARY KEY (stadium_tel_code, date, race_number, pit_number);
ALTER TABLE ONLY public.disqualified_race_entries
    ADD CONSTRAINT disqualified_race_entries_pkey PRIMARY KEY (stadium_tel_code, date, race_number, pit_number);
ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_pkey PRIMARY KEY (stadium_tel_code, starts_on, title);
ALTER TABLE ONLY public.motor_betting_contribute_rate_aggregations
    ADD CONSTRAINT motor_betting_contribute_rate_aggregations_pkey PRIMARY KEY (stadium_tel_code, motor_number, aggregated_on);
ALTER TABLE ONLY public.motor_maintenances
    ADD CONSTRAINT motor_maintenances_pkey PRIMARY KEY (stadium_tel_code, date, race_number, motor_number, exchanged_parts);
ALTER TABLE ONLY public.motor_renewals
    ADD CONSTRAINT motor_renewals_pkey PRIMARY KEY (stadium_tel_code, date);
ALTER TABLE ONLY public.odds
    ADD CONSTRAINT odds_pkey PRIMARY KEY (stadium_tel_code, date, race_number, betting_method, betting_number);
ALTER TABLE ONLY public.payoffs
    ADD CONSTRAINT payoffs_pkey PRIMARY KEY (stadium_tel_code, date, race_number, betting_method, betting_number);
ALTER TABLE ONLY public.race_entries
    ADD CONSTRAINT race_entries_pkey PRIMARY KEY (stadium_tel_code, date, race_number, pit_number);
ALTER TABLE ONLY public.race_records
    ADD CONSTRAINT race_records_pkey PRIMARY KEY (stadium_tel_code, date, race_number, pit_number);
ALTER TABLE ONLY public.racer_conditions
    ADD CONSTRAINT racer_conditions_pkey PRIMARY KEY (racer_registration_number, date);
ALTER TABLE ONLY public.racer_winning_rate_aggregations
    ADD CONSTRAINT racer_winning_rate_aggregations_pkey PRIMARY KEY (racer_registration_number, aggregated_on);
ALTER TABLE ONLY public.racers
    ADD CONSTRAINT racers_pkey PRIMARY KEY (registration_number);
ALTER TABLE ONLY public.races
    ADD CONSTRAINT races_pkey PRIMARY KEY (stadium_tel_code, date, race_number);
ALTER TABLE ONLY public.stadiums
    ADD CONSTRAINT stadiums_pkey PRIMARY KEY (tel_code);
ALTER TABLE ONLY public.start_exhibition_records
    ADD CONSTRAINT start_exhibition_records_pkey PRIMARY KEY (stadium_tel_code, date, race_number, pit_number);
ALTER TABLE ONLY public.race_entries
    ADD CONSTRAINT uniq_index_1 UNIQUE (stadium_tel_code, date, race_number, racer_registration_number);
ALTER TABLE ONLY public.weather_conditions
    ADD CONSTRAINT weather_conditions_pkey PRIMARY KEY (stadium_tel_code, date, race_number, is_in_performance);
ALTER TABLE ONLY public.winning_race_entries
    ADD CONSTRAINT winning_race_entries_pkey PRIMARY KEY (stadium_tel_code, date, race_number, pit_number);
ALTER TABLE ONLY public.boat_betting_contribute_rate_aggregations
    ADD CONSTRAINT boat_betting_contribute_rate_aggregations_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.boat_settings
    ADD CONSTRAINT boat_settings_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.circumference_exhibition_records
    ADD CONSTRAINT circumference_exhibition_records_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.disqualified_race_entries
    ADD CONSTRAINT disqualified_race_entries_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.events
    ADD CONSTRAINT events_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.motor_betting_contribute_rate_aggregations
    ADD CONSTRAINT motor_betting_contribute_rate_aggregation_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.motor_maintenances
    ADD CONSTRAINT motor_maintenances_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.motor_renewals
    ADD CONSTRAINT motor_renewals_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.odds
    ADD CONSTRAINT odds_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.payoffs
    ADD CONSTRAINT payoffs_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.race_entries
    ADD CONSTRAINT race_entries_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.race_records
    ADD CONSTRAINT race_records_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.races
    ADD CONSTRAINT races_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.start_exhibition_records
    ADD CONSTRAINT start_exhibition_records_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.weather_conditions
    ADD CONSTRAINT weather_conditions_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
ALTER TABLE ONLY public.winning_race_entries
    ADD CONSTRAINT winning_race_entries_stadium_tel_code_fkey FOREIGN KEY (stadium_tel_code) REFERENCES public.stadiums(tel_code);
