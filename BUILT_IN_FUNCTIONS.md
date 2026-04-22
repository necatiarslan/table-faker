These lists are generated from the current runtime context used by tablefaker (`fake = Faker('en_US')`, Python `random` module).
Total `fake.` callables: **292**
Total `random.` callables: **27**

### `random.` functions

| Function | Signature |
|---|---|
| `random.Random` | `(x=None)` |
| `random.SystemRandom` | `(x=None)` |
| `random.betavariate` | `(alpha, beta)` |
| `random.binomialvariate` | `(n=1, p=0.5)` |
| `random.choice` | `(seq)` |
| `random.choices` | `(population, weights=None, *, cum_weights=None, k=1)` |
| `random.expovariate` | `(lambd=1.0)` |
| `random.gammavariate` | `(alpha, beta)` |
| `random.gauss` | `(mu=0.0, sigma=1.0)` |
| `random.getrandbits` | `(k, /)` |
| `random.getstate` | `()` |
| `random.lognormvariate` | `(mu, sigma)` |
| `random.main` | `(arg_list: list[str] \| None = None) -> int \| str` |
| `random.normalvariate` | `(mu=0.0, sigma=1.0)` |
| `random.paretovariate` | `(alpha)` |
| `random.randbytes` | `(n)` |
| `random.randint` | `(a, b)` |
| `random.random` | `()` |
| `random.randrange` | `(start, stop=None, step=1)` |
| `random.sample` | `(population, k, *, counts=None)` |
| `random.seed` | `(a=None, version=2)` |
| `random.setstate` | `(state)` |
| `random.shuffle` | `(x)` |
| `random.triangular` | `(low=0.0, high=1.0, mode=None)` |
| `random.uniform` | `(a, b)` |
| `random.vonmisesvariate` | `(mu, kappa)` |
| `random.weibullvariate` | `(alpha, beta)` |

### `fake.` functions

| Function | Signature |
|---|---|
| `fake.aba` | `() -> str` |
| `fake.add_provider` | `(provider: Union[ForwardRef('BaseProvider'), Type[ForwardRef('BaseProvider')]]) -> None` |
| `fake.address` | `() -> str` |
| `fake.administrative_unit` | `() -> str` |
| `fake.am_pm` | `() -> str` |
| `fake.android_platform_token` | `() -> str` |
| `fake.ascii_company_email` | `() -> str` |
| `fake.ascii_email` | `() -> str` |
| `fake.ascii_free_email` | `() -> str` |
| `fake.ascii_safe_email` | `() -> str` |
| `fake.bank_country` | `() -> str` |
| `fake.basic_phone_number` | `() -> str` |
| `fake.bban` | `() -> str` |
| `fake.binary` | `(length: int = 1048576) -> bytes` |
| `fake.boolean` | `(chance_of_getting_true: int = 50) -> bool` |
| `fake.bothify` | `(text: str = '## ??', letters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') -> str` |
| `fake.bs` | `() -> str` |
| `fake.building_number` | `() -> str` |
| `fake.catch_phrase` | `() -> str` |
| `fake.century` | `() -> str` |
| `fake.chrome` | `(version_from: int = 13, version_to: int = 63, build_from: int = 800, build_to: int = 899) -> str` |
| `fake.city` | `() -> str` |
| `fake.city_prefix` | `() -> str` |
| `fake.city_suffix` | `() -> str` |
| `fake.color` | `(hue: Union[str, float, int, Sequence[int], NoneType] = None, luminosity: Optional[str] = None, color_format: str = 'hex') -> str` |
| `fake.color_hsl` | `(hue: Union[str, float, int, Sequence[int], NoneType] = None, luminosity: Optional[str] = None) -> Tuple[int, int, int]` |
| `fake.color_hsv` | `(hue: Union[str, float, int, Sequence[int], NoneType] = None, luminosity: Optional[str] = None) -> Tuple[int, int, int]` |
| `fake.color_name` | `() -> str` |
| `fake.color_rgb` | `(hue: Union[str, float, int, Sequence[int], NoneType] = None, luminosity: Optional[str] = None) -> Tuple[int, int, int]` |
| `fake.color_rgb_float` | `(hue: Union[str, float, int, Sequence[int], NoneType] = None, luminosity: Optional[str] = None) -> Tuple[float, float, float]` |
| `fake.company` | `() -> str` |
| `fake.company_email` | `() -> str` |
| `fake.company_suffix` | `() -> str` |
| `fake.coordinate` | `(center: Optional[float] = None, radius: Union[float, int] = 0.001) -> decimal.Decimal` |
| `fake.country` | `() -> str` |
| `fake.country_calling_code` | `() -> str` |
| `fake.country_code` | `(representation: str = 'alpha-2') -> str` |
| `fake.credit_card_expire` | `(start: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = 'now', end: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '+10y', date_format: str = '%m/%y') -> str` |
| `fake.credit_card_full` | `(card_type: Optional[~CardType] = None) -> str` |
| `fake.credit_card_number` | `(card_type: Optional[~CardType] = None) -> str` |
| `fake.credit_card_provider` | `(card_type: Optional[~CardType] = None) -> str` |
| `fake.credit_card_security_code` | `(card_type: Optional[~CardType] = None) -> str` |
| `fake.cryptocurrency` | `() -> Tuple[str, str]` |
| `fake.cryptocurrency_code` | `() -> str` |
| `fake.cryptocurrency_name` | `() -> str` |
| `fake.csv` | `(header: Optional[Sequence[str]] = None, data_columns: Tuple[str, str] = ('{{name}}', '{{address}}'), num_rows: int = 10, include_row_ids: bool = False) -> str` |
| `fake.currency` | `() -> Tuple[str, str]` |
| `fake.currency_code` | `() -> str` |
| `fake.currency_name` | `() -> str` |
| `fake.currency_symbol` | `(code: Optional[str] = None) -> str` |
| `fake.current_country` | `() -> str` |
| `fake.current_country_code` | `() -> str` |
| `fake.date` | `(pattern: str = '%Y-%m-%d', end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> str` |
| `fake.date_between` | `(start_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '-30y', end_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = 'today') -> datetime.date` |
| `fake.date_between_dates` | `(date_start: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None, date_end: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> datetime.date` |
| `fake.date_object` | `(end_datetime: Optional[datetime.datetime] = None) -> datetime.date` |
| `fake.date_of_birth` | `(tzinfo: Optional[datetime.tzinfo] = None, minimum_age: int = 0, maximum_age: int = 115) -> datetime.date` |
| `fake.date_this_century` | `(before_today: bool = True, after_today: bool = False) -> datetime.date` |
| `fake.date_this_decade` | `(before_today: bool = True, after_today: bool = False) -> datetime.date` |
| `fake.date_this_month` | `(before_today: bool = True, after_today: bool = False) -> datetime.date` |
| `fake.date_this_year` | `(before_today: bool = True, after_today: bool = False) -> datetime.date` |
| `fake.date_time` | `(tzinfo: Optional[datetime.tzinfo] = None, end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> datetime.datetime` |
| `fake.date_time_ad` | `(tzinfo: Optional[datetime.tzinfo] = None, end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None, start_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> datetime.datetime` |
| `fake.date_time_between` | `(start_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '-30y', end_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = 'now', tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.date_time_between_dates` | `(datetime_start: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None, datetime_end: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None, tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.date_time_this_century` | `(before_now: bool = True, after_now: bool = False, tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.date_time_this_decade` | `(before_now: bool = True, after_now: bool = False, tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.date_time_this_month` | `(before_now: bool = True, after_now: bool = False, tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.date_time_this_year` | `(before_now: bool = True, after_now: bool = False, tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.day_of_month` | `() -> str` |
| `fake.day_of_week` | `() -> str` |
| `fake.del_arguments` | `(group: str, argument: Optional[str] = None) -> Any` |
| `fake.dga` | `(year: Optional[int] = None, month: Optional[int] = None, day: Optional[int] = None, tld: Optional[str] = None, length: Optional[int] = None) -> str` |
| `fake.doi` | `() -> str` |
| `fake.domain_name` | `(levels: int = 1) -> str` |
| `fake.domain_word` | `() -> str` |
| `fake.dsv` | `(dialect: str = 'faker-csv', header: Optional[Sequence[str]] = None, data_columns: Tuple[str, str] = ('{{name}}', '{{address}}'), num_rows: int = 10, include_row_ids: bool = False, **fmtparams: Any) -> str` |
| `fake.ean` | `(length: int = 13, prefixes: Tuple[Union[int, str, Tuple[Union[int, str], ...]], ...] = ()) -> str` |
| `fake.ean13` | `(prefixes: Tuple[Union[int, str, Tuple[Union[int, str], ...]], ...] = (), leading_zero: Optional[bool] = None) -> str` |
| `fake.ean8` | `(prefixes: Tuple[Union[int, str, Tuple[Union[int, str], ...]], ...] = ()) -> str` |
| `fake.ein` | `() -> str` |
| `fake.email` | `(safe: bool = True, domain: Optional[str] = None) -> str` |
| `fake.emoji` | `() -> str` |
| `fake.enum` | `(enum_cls: Type[~TEnum]) -> ~TEnum` |
| `fake.file_extension` | `(category: Optional[str] = None) -> str` |
| `fake.file_name` | `(category: Optional[str] = None, extension: Optional[str] = None) -> str` |
| `fake.file_path` | `(depth: int = 1, category: Optional[str] = None, extension: Union[str, Sequence[str], NoneType] = None, absolute: Optional[bool] = True, file_system_rule: Literal['linux', 'windows'] = 'linux') -> str` |
| `fake.firefox` | `() -> str` |
| `fake.first_name` | `() -> str` |
| `fake.first_name_female` | `() -> str` |
| `fake.first_name_male` | `() -> str` |
| `fake.first_name_nonbinary` | `() -> str` |
| `fake.fixed_width` | `(data_columns: Optional[List[Union[Tuple[int, str], Tuple[int, str, Dict[str, Any]]]]] = None, num_rows: int = 10, align: str = 'left') -> str` |
| `fake.format` | `(formatter: str, *args: Any, **kwargs: Any) -> str` |
| `fake.free_email` | `() -> str` |
| `fake.free_email_domain` | `() -> str` |
| `fake.future_date` | `(end_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '+30d') -> datetime.date` |
| `fake.future_datetime` | `(end_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '+30d', tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.get_arguments` | `(group: str, argument: Optional[str] = None) -> Any` |
| `fake.get_formatter` | `(formatter: str) -> Callable` |
| `fake.get_providers` | `() -> List[ForwardRef('BaseProvider')]` |
| `fake.get_words_list` | `(part_of_speech: Optional[str] = None, ext_word_list: Optional[Sequence[str]] = None) -> List[str]` |
| `fake.hex_color` | `() -> str` |
| `fake.hexify` | `(text: str = '^^^^', upper: bool = False) -> str` |
| `fake.hostname` | `(levels: int = 1) -> str` |
| `fake.http_method` | `() -> str` |
| `fake.http_status_code` | `(include_unassigned: bool = True) -> int` |
| `fake.iana_id` | `() -> str` |
| `fake.iban` | `() -> str` |
| `fake.image` | `(size: Tuple[int, int] = (256, 256), image_format: str = 'png', hue: Union[int, Sequence[int], str, NoneType] = None, luminosity: Optional[str] = None) -> bytes` |
| `fake.image_url` | `(width: Optional[int] = None, height: Optional[int] = None, placeholder_url: Optional[str] = None) -> str` |
| `fake.internet_explorer` | `() -> str` |
| `fake.invalid_ssn` | `() -> str` |
| `fake.ios_platform_token` | `() -> str` |
| `fake.ipv4` | `(network: bool = False, address_class: Optional[str] = None, private: Optional[str] = None) -> str` |
| `fake.ipv4_network_class` | `() -> str` |
| `fake.ipv4_private` | `(network: bool = False, address_class: Optional[str] = None) -> str` |
| `fake.ipv4_public` | `(network: bool = False, address_class: Optional[str] = None) -> str` |
| `fake.ipv6` | `(network: bool = False) -> str` |
| `fake.isbn10` | `(separator: str = '-') -> str` |
| `fake.isbn13` | `(separator: str = '-') -> str` |
| `fake.iso8601` | `(tzinfo: Optional[datetime.tzinfo] = None, end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None, sep: str = 'T', timespec: str = 'auto') -> str` |
| `fake.items` | `() -> 'list[tuple[str, Generator \| Faker]]'` |
| `fake.itin` | `() -> str` |
| `fake.job` | `() -> str` |
| `fake.job_female` | `() -> str` |
| `fake.job_male` | `() -> str` |
| `fake.json` | `(data_columns: Optional[List] = None, num_rows: int = 10, indent: Optional[int] = None, cls: Optional[Type[json.encoder.JSONEncoder]] = None) -> str` |
| `fake.json_bytes` | `(data_columns: Optional[List] = None, num_rows: int = 10, indent: Optional[int] = None, cls: Optional[Type[json.encoder.JSONEncoder]] = None) -> bytes` |
| `fake.language_code` | `() -> str` |
| `fake.language_name` | `() -> str` |
| `fake.last_name` | `() -> str` |
| `fake.last_name_female` | `() -> str` |
| `fake.last_name_male` | `() -> str` |
| `fake.last_name_nonbinary` | `() -> str` |
| `fake.latitude` | `() -> decimal.Decimal` |
| `fake.latlng` | `() -> Tuple[decimal.Decimal, decimal.Decimal]` |
| `fake.lexify` | `(text: str = '????', letters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') -> str` |
| `fake.license_plate` | `() -> str` |
| `fake.linux_platform_token` | `() -> str` |
| `fake.linux_processor` | `() -> str` |
| `fake.local_latlng` | `(country_code: str = 'US', coords_only: bool = False) -> Optional[Tuple[str, ...]]` |
| `fake.locale` | `() -> str` |
| `fake.localized_ean` | `(length: int = 13) -> str` |
| `fake.localized_ean13` | `() -> str` |
| `fake.localized_ean8` | `() -> str` |
| `fake.location_on_land` | `(coords_only: bool = False) -> Tuple[str, ...]` |
| `fake.longitude` | `() -> decimal.Decimal` |
| `fake.mac_address` | `(multicast: bool = False) -> str` |
| `fake.mac_platform_token` | `() -> str` |
| `fake.mac_processor` | `() -> str` |
| `fake.md5` | `(raw_output: bool = False) -> Union[bytes, str]` |
| `fake.military_apo` | `() -> str` |
| `fake.military_dpo` | `() -> str` |
| `fake.military_ship` | `() -> str` |
| `fake.military_state` | `() -> str` |
| `fake.mime_type` | `(category: Optional[str] = None) -> str` |
| `fake.month` | `() -> str` |
| `fake.month_name` | `() -> str` |
| `fake.msisdn` | `() -> str` |
| `fake.name` | `() -> str` |
| `fake.name_female` | `() -> str` |
| `fake.name_male` | `() -> str` |
| `fake.name_nonbinary` | `() -> str` |
| `fake.nic_handle` | `(suffix: str = 'FAKE') -> str` |
| `fake.nic_handles` | `(count: int = 1, suffix: str = '????') -> List[str]` |
| `fake.null_boolean` | `() -> Optional[bool]` |
| `fake.numerify` | `(text: str = '###') -> str` |
| `fake.opera` | `() -> str` |
| `fake.paragraph` | `(nb_sentences: int = 3, variable_nb_sentences: bool = True, ext_word_list: Optional[Sequence[str]] = None) -> str` |
| `fake.paragraphs` | `(nb: int = 3, ext_word_list: Optional[Sequence[str]] = None) -> List[str]` |
| `fake.parse` | `(text: str) -> str` |
| `fake.passport_dates` | `(birthday: datetime.date = datetime.date(2026, 4, 22)) -> Tuple[str, str, str]` |
| `fake.passport_dob` | `() -> datetime.date` |
| `fake.passport_full` | `() -> str` |
| `fake.passport_gender` | `(seed: int = 0) -> Literal['M', 'F', 'X']` |
| `fake.passport_number` | `() -> str` |
| `fake.passport_owner` | `(gender: Literal['M', 'F', 'X'] = 'X') -> Tuple[str, str]` |
| `fake.password` | `(length: int = 10, special_chars: bool = True, digits: bool = True, upper_case: bool = True, lower_case: bool = True) -> str` |
| `fake.past_date` | `(start_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '-30d', tzinfo: Optional[datetime.tzinfo] = None) -> datetime.date` |
| `fake.past_datetime` | `(start_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '-30d', tzinfo: Optional[datetime.tzinfo] = None) -> datetime.datetime` |
| `fake.phone_number` | `() -> str` |
| `fake.port_number` | `(is_system: bool = False, is_user: bool = False, is_dynamic: bool = False) -> int` |
| `fake.postalcode` | `() -> str` |
| `fake.postalcode_in_state` | `(state_abbr: Optional[str] = None) -> str` |
| `fake.postalcode_plus4` | `() -> str` |
| `fake.postcode` | `() -> str` |
| `fake.postcode_in_state` | `(state_abbr: Optional[str] = None) -> str` |
| `fake.prefix` | `() -> str` |
| `fake.prefix_female` | `() -> str` |
| `fake.prefix_male` | `() -> str` |
| `fake.prefix_nonbinary` | `() -> str` |
| `fake.pricetag` | `() -> str` |
| `fake.profile` | `(fields: Optional[List[str]] = None, sex: Optional[Literal['M', 'F', 'X']] = None) -> Dict[str, Union[str, Tuple[decimal.Decimal, decimal.Decimal], List[str], datetime.date]]` |
| `fake.provider` | `(name: str) -> Optional[ForwardRef('BaseProvider')]` |
| `fake.psv` | `(header: Optional[Sequence[str]] = None, data_columns: Tuple[str, str] = ('{{name}}', '{{address}}'), num_rows: int = 10, include_row_ids: bool = False) -> str` |
| `fake.pybool` | `(truth_probability: int = 50) -> bool` |
| `fake.pydecimal` | `(left_digits: Optional[int] = None, right_digits: Optional[int] = None, positive: Optional[bool] = None, min_value: Union[float, int, NoneType] = None, max_value: Union[float, int, NoneType] = None) -> decimal.Decimal` |
| `fake.pydict` | `(nb_elements: int = 10, variable_nb_elements: bool = True, value_types: Union[List[Type], Tuple[Type, ...], NoneType] = None, allowed_types: Union[List[Type], Tuple[Type, ...], NoneType] = None) -> Dict[Any, Any]` |
| `fake.pyfloat` | `(left_digits: Optional[int] = None, right_digits: Optional[int] = None, positive: Optional[bool] = None, min_value: Union[float, int, NoneType] = None, max_value: Union[float, int, NoneType] = None) -> float` |
| `fake.pyint` | `(min_value: int = 0, max_value: int = 9999, step: int = 1) -> int` |
| `fake.pyiterable` | `(nb_elements: int = 10, variable_nb_elements: bool = True, value_types: Union[List[Type], Tuple[Type, ...], NoneType] = None, allowed_types: Union[List[Type], Tuple[Type, ...], NoneType] = None) -> Iterable[Any]` |
| `fake.pylist` | `(nb_elements: int = 10, variable_nb_elements: bool = True, value_types: Union[List[Type], Tuple[Type, ...], NoneType] = None, allowed_types: Union[List[Type], Tuple[Type, ...], NoneType] = None) -> List[Any]` |
| `fake.pyobject` | `(object_type: Optional[Type[Union[bool, str, float, int, tuple, set, list, Iterable, dict]]] = None) -> Union[bool, str, float, int, tuple, set, list, Iterable, dict, NoneType]` |
| `fake.pyset` | `(nb_elements: int = 10, variable_nb_elements: bool = True, value_types: Union[List[Type], Tuple[Type, ...], NoneType] = None, allowed_types: Union[List[Type], Tuple[Type, ...], NoneType] = None) -> Set[Any]` |
| `fake.pystr` | `(min_chars: Optional[int] = None, max_chars: int = 20, prefix: str = '', suffix: str = '') -> str` |
| `fake.pystr_format` | `(string_format: str = '?#-###{{random_int}}{{random_letter}}', letters: str = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ') -> str` |
| `fake.pystruct` | `(count: int = 10, value_types: Union[List[Type], Tuple[Type, ...], NoneType] = None, allowed_types: Union[List[Type], Tuple[Type, ...], NoneType] = None) -> Tuple[List, Dict, Dict]` |
| `fake.pytimezone` | `(*args: Any, **kwargs: Any) -> Optional[datetime.tzinfo]` |
| `fake.pytuple` | `(nb_elements: int = 10, variable_nb_elements: bool = True, value_types: Union[List[Type], Tuple[Type, ...], NoneType] = None, allowed_types: Union[List[Type], Tuple[Type, ...], NoneType] = None) -> Tuple[Any, ...]` |
| `fake.random_choices` | `(elements: Union[Collection[~T], collections.OrderedDict[~T, float]] = ('a', 'b', 'c'), length: Optional[int] = None) -> Sequence[~T]` |
| `fake.random_digit` | `() -> int` |
| `fake.random_digit_above_two` | `() -> int` |
| `fake.random_digit_not_null` | `() -> int` |
| `fake.random_digit_not_null_or_empty` | `() -> Union[int, str]` |
| `fake.random_digit_or_empty` | `() -> Union[int, str]` |
| `fake.random_element` | `(elements: Union[Collection[~T], collections.OrderedDict[~T, float]] = ('a', 'b', 'c')) -> ~T` |
| `fake.random_elements` | `(elements: Union[Collection[~T], collections.OrderedDict[~T, float]] = ('a', 'b', 'c'), length: Optional[int] = None, unique: bool = False, use_weighting: Optional[bool] = None) -> Sequence[~T]` |
| `fake.random_int` | `(min: int = 0, max: int = 9999, step: int = 1) -> int` |
| `fake.random_letter` | `() -> str` |
| `fake.random_letters` | `(length: int = 16) -> Sequence[str]` |
| `fake.random_lowercase_letter` | `() -> str` |
| `fake.random_number` | `(digits: Optional[int] = None, fix_len: bool = False) -> int` |
| `fake.random_sample` | `(elements: Union[Collection[~T], collections.OrderedDict[~T, float]] = ('a', 'b', 'c'), length: Optional[int] = None) -> Sequence[~T]` |
| `fake.random_uppercase_letter` | `() -> str` |
| `fake.randomize_nb_elements` | `(number: int = 10, le: bool = False, ge: bool = False, min: Optional[int] = None, max: Optional[int] = None) -> int` |
| `fake.rgb_color` | `() -> str` |
| `fake.rgb_css_color` | `() -> str` |
| `fake.ripe_id` | `() -> str` |
| `fake.safari` | `() -> str` |
| `fake.safe_color_name` | `() -> str` |
| `fake.safe_domain_name` | `() -> str` |
| `fake.safe_email` | `() -> str` |
| `fake.safe_hex_color` | `() -> str` |
| `fake.sbn9` | `(separator: str = '-') -> str` |
| `fake.secondary_address` | `() -> str` |
| `fake.seed_instance` | `(seed: 'SeedType \| None' = None) -> 'None'` |
| `fake.seed_locale` | `(locale: 'str', seed: 'SeedType \| None' = None) -> 'None'` |
| `fake.sentence` | `(nb_words: int = 6, variable_nb_words: bool = True, ext_word_list: Optional[Sequence[str]] = None) -> str` |
| `fake.sentences` | `(nb: int = 3, ext_word_list: Optional[Sequence[str]] = None) -> List[str]` |
| `fake.set_arguments` | `(group: str, argument: str, value: Optional[Any] = None) -> None` |
| `fake.set_formatter` | `(name: str, formatter: Callable) -> None` |
| `fake.sha1` | `(raw_output: bool = False) -> Union[bytes, str]` |
| `fake.sha256` | `(raw_output: bool = False) -> Union[bytes, str]` |
| `fake.simple_profile` | `(sex: Optional[Literal['M', 'F', 'X']] = None) -> Dict[str, Union[str, datetime.date, Literal['M', 'F', 'X']]]` |
| `fake.slug` | `(value: Optional[str] = None) -> str` |
| `fake.ssn` | `(taxpayer_identification_number_type: str = 'SSN') -> str` |
| `fake.state` | `() -> str` |
| `fake.state_abbr` | `(include_territories: bool = True, include_freely_associated_states: bool = True) -> str` |
| `fake.street_address` | `() -> str` |
| `fake.street_name` | `() -> str` |
| `fake.street_suffix` | `() -> str` |
| `fake.suffix` | `() -> str` |
| `fake.suffix_female` | `() -> str` |
| `fake.suffix_male` | `() -> str` |
| `fake.suffix_nonbinary` | `() -> str` |
| `fake.swift` | `(length: Optional[int] = None, primary: bool = False, use_dataset: bool = False) -> str` |
| `fake.swift11` | `(primary: bool = False, use_dataset: bool = False) -> str` |
| `fake.swift8` | `(use_dataset: bool = False) -> str` |
| `fake.tar` | `(uncompressed_size: int = 65536, num_files: int = 1, min_file_size: int = 4096, compression: Optional[str] = None) -> bytes` |
| `fake.text` | `(max_nb_chars: int = 200, ext_word_list: Optional[Sequence[str]] = None) -> str` |
| `fake.texts` | `(nb_texts: int = 3, max_nb_chars: int = 200, ext_word_list: Optional[Sequence[str]] = None) -> List[str]` |
| `fake.time` | `(pattern: str = '%H:%M:%S', end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> str` |
| `fake.time_delta` | `(end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> datetime.timedelta` |
| `fake.time_object` | `(end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> datetime.time` |
| `fake.time_series` | `(start_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = '-30d', end_date: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int] = 'now', precision: Optional[float] = None, distrib: Optional[Callable[[datetime.datetime], float]] = None, tzinfo: Optional[datetime.tzinfo] = None) -> Iterator[Tuple[datetime.datetime, Any]]` |
| `fake.timezone` | `() -> str` |
| `fake.tld` | `() -> str` |
| `fake.tsv` | `(header: Optional[Sequence[str]] = None, data_columns: Tuple[str, str] = ('{{name}}', '{{address}}'), num_rows: int = 10, include_row_ids: bool = False) -> str` |
| `fake.unix_device` | `(prefix: Optional[str] = None) -> str` |
| `fake.unix_partition` | `(prefix: Optional[str] = None) -> str` |
| `fake.unix_time` | `(end_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None, start_datetime: Union[datetime.date, datetime.datetime, datetime.timedelta, str, int, NoneType] = None) -> float` |
| `fake.upc_a` | `(upc_ae_mode: bool = False, base: Optional[str] = None, number_system_digit: Optional[int] = None) -> str` |
| `fake.upc_e` | `(base: Optional[str] = None, number_system_digit: Optional[int] = None, safe_mode: bool = True) -> str` |
| `fake.uri` | `(schemes: Optional[List[str]] = None, deep: Optional[int] = None) -> str` |
| `fake.uri_extension` | `() -> str` |
| `fake.uri_page` | `() -> str` |
| `fake.uri_path` | `(deep: Optional[int] = None) -> str` |
| `fake.url` | `(schemes: Optional[List[str]] = None) -> str` |
| `fake.user_agent` | `() -> str` |
| `fake.user_name` | `() -> str` |
| `fake.uuid4` | `(cast_to: Union[Callable[[uuid.UUID], str], Callable[[uuid.UUID], bytes], NoneType] = <class 'str'>) -> Union[bytes, str, uuid.UUID]` |
| `fake.vin` | `() -> str` |
| `fake.windows_platform_token` | `() -> str` |
| `fake.word` | `(part_of_speech: Optional[str] = None, ext_word_list: Optional[Sequence[str]] = None) -> str` |
| `fake.words` | `(nb: int = 3, ext_word_list: Optional[List[str]] = None, part_of_speech: Optional[str] = None, unique: bool = False) -> List[str]` |
| `fake.xml` | `(nb_elements: int = 10, variable_nb_elements: bool = True, value_types: Union[List[Type], Tuple[Type, ...], NoneType] = None, allowed_types: Union[List[Type], Tuple[Type, ...], NoneType] = None) -> str` |
| `fake.year` | `() -> str` |
| `fake.zip` | `(uncompressed_size: int = 65536, num_files: int = 1, min_file_size: int = 4096, compression: Optional[str] = None) -> bytes` |
| `fake.zipcode` | `() -> str` |
| `fake.zipcode_in_state` | `(state_abbr: Optional[str] = None) -> str` |
| `fake.zipcode_plus4` | `() -> str` |