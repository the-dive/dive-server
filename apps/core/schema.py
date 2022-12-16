import graphene
from graphene_django import DjangoObjectType, DjangoListField
from graphene_django_extras import PageGraphqlPagination, DjangoObjectField

from utils.graphene.types import CustomDjangoListObjectType
from utils.graphene.fields import DjangoPaginatedListObjectField
from utils.graphene.enums import EnumDescription

from apps.core.models import (
    Dataset,
    Table,
)
from apps.core.filter_set import DatasetFilter


class TableType(DjangoObjectType):
    class Meta:
        model = Table
        only_fields = ("id", "name", "status", "is_added_to_workspace")
        skip_registry = True

    status_display = EnumDescription(source="get_status_display")


class DatasetType(DjangoObjectType):
    class Meta:
        model = Dataset
        fields = (
            "id",
            "name",
            "status",
        )
        skip_registry = True

    tables = DjangoListField(TableType)
    file = graphene.ID(source="file_id", required=True)
    status_display = EnumDescription(source="get_status_display")


class DatasetDetailType(DatasetType):
    class Meta:
        model = Dataset
        fields = "__all__"


class DatasetListType(CustomDjangoListObjectType):
    class Meta:
        model = Dataset
        filterset_class = DatasetFilter


class KeyValueType(graphene.ObjectType):
    key = graphene.String()
    label = graphene.String()


class TablePropertiesType(graphene.ObjectType):
    headers = graphene.List(KeyValueType)
    languages = graphene.List(KeyValueType)
    time_zones = graphene.List(KeyValueType)

    def resolve_headers(self, info):
        data = [
            {
                "key": "1",
                "label": "One",
            },
            {
                "key": "1",
                "label": "One",
            },
            {
                "key": "1",
                "label": "One",
            },
            {
                "key": "1",
                "label": "One",
            },
            {
                "key": "1",
                "label": "One",
            },
        ]
        output = []
        for d in data:
            output.append(
                KeyValueType(
                    key=d["key"],
                    label=d["label"],
                )
            )
        return output

    def resolve_languages(self, info):
        data = [
            {
                "key": "english_us",
                "label": "English(US)",
            },
            {
                "key": "english_uk",
                "label": "English(UK)",
            },
            {
                "key": "english_aus",
                "label": "English(AUS)",
            },
            {
                "key": "spanish",
                "label": "Spanish",
            },
            {
                "key": "french",
                "label": "French",
            },
            {
                "key": "Arabic",
                "label": "Arabic",
            },
        ]
        output = []
        for d in data:
            output.append(
                KeyValueType(
                    key=d["key"],
                    label=d["label"],
                )
            )
        return output

    def resolve_time_zones(self, info):
        timezone_list = [
            "(UTC+04:30)Afghanistan",
            "(UTC+02:00)Åland Islands",
            "(UTC+01:00)Albania",
            "(UTC+01:00)Algeria",
            "(UTC-11:00)American Samoa",
            "(UTC+01:00)Andorra",
            "(UTC+01:00)Angola",
            "(UTC-04:00)Anguilla",
            "(UTC-03:00)Antarctica",
            "(UTC-04:00)Antigua and Barbuda",
            "(UTC-03:00)Argentina",
            "(UTC+04:00)Armenia",
            "(UTC-04:00)Aruba",
            "(UTC+10:00)Australia",
            "(UTC+01:00)Austria",
            "(UTC+04:00)Azerbaijan",
            "(UTC-05:00)Bahamas",
            "(UTC+03:00)Bahrain",
            "(UTC+06:00)Bangladesh",
            "(UTC-04:00)Barbados",
            "(UTC+03:00)Belarus",
            "(UTC+01:00)Belgium",
            "(UTC-06:00)Belize",
            "(UTC+01:00)Benin",
            "(UTC-04:00)Bermuda",
            "(UTC+06:00)Bhutan",
            "(UTC-04:30)Bolivarian Republic of Venezuela",
            "(UTC-04:00)Bolivia",
            "(UTC-04:00)Bonaire, Sint Eustatius and Saba",
            "(UTC+01:00)Bosnia and Herzegovina",
            "(UTC+02:00)Botswana",
            "(UTC)Bouvet Island",
            "(UTC-03:00)Brazil",
            "(UTC+06:00)British Indian Ocean Territory",
            "(UTC+08:00)Brunei",
            "(UTC+02:00)Bulgaria",
            "(UTC)Burkina Faso",
            "(UTC+02:00)Burundi",
            "(UTC-01:00)Cabo Verde",
            "(UTC+07:00)Cambodia",
            "(UTC+01:00)Cameroon",
            "(UTC-05:00)Canada",
            "(UTC-05:00)Cayman Islands",
            "(UTC+01:00)Central African Republic",
            "(UTC+01:00)Chad",
            "(UTC-03:00)Chile",
            "(UTC+08:00)China",
            "(UTC+07:00)Christmas Island",
            "(UTC+06:30)Cocos (Keeling) Islands",
            "(UTC-05:00)Colombia",
            "(UTC+03:00)Comoros",
            "(UTC+01:00)Congo",
            "(UTC+01:00)Congo (DRC)",
            "(UTC-10:00)Cook Islands",
            "(UTC-06:00)Costa Rica",
            "(UTC+01:00)Croatia",
            "(UTC-05:00)Cuba",
            "(UTC-04:00)Curaçao",
            "(UTC+02:00)Cyprus",
            "(UTC+01:00)Czech Republic",
            "(UTC+09:00)Democratic Republic of Timor-Leste",
            "(UTC+01:00)Denmark",
            "(UTC+03:00)Djibouti",
            "(UTC-04:00)Dominica",
            "(UTC-04:00)Dominican Republic",
            "(UTC-05:00)Ecuador",
            "(UTC+02:00)Egypt",
            "(UTC-06:00)El Salvador",
            "(UTC+01:00)Equatorial Guinea",
            "(UTC+03:00)Eritrea",
            "(UTC+02:00)Estonia",
            "(UTC+03:00)Ethiopia",
            "(UTC-03:00)Falkland Islands (Islas Malvinas)",
            "(UTC)Faroe Islands",
            "(UTC+12:00)Fiji Islands",
            "(UTC+02:00)Finland",
            "(UTC+01:00)France",
            "(UTC-03:00)French Guiana",
            "(UTC-10:00)French Polynesia",
            "(UTC+05:00)French Southern and Antarctic Lands",
            "(UTC+01:00)Gabon",
            "(UTC)Gambia",
            "(UTC+04:00)Georgia",
            "(UTC+01:00)Germany",
            "(UTC)Ghana",
            "(UTC+01:00)Gibraltar",
            "(UTC+02:00)Greece",
            "(UTC-03:00)Greenland",
            "(UTC-04:00)Grenada",
            "(UTC-04:00)Guadeloupe",
            "(UTC+10:00)Guam",
            "(UTC-06:00)Guatemala",
            "(UTC)Guernsey",
            "(UTC)Guinea",
            "(UTC)Guinea-Bissau",
            "(UTC-04:00)Guyana",
            "(UTC-05:00)Haiti",
            "(UTC+04:00)Heard Island and McDonald Islands",
            "(UTC-06:00)Honduras",
            "(UTC+08:00)Hong Kong SAR" "(UTC+01:00)Hungary",
            "(UTC)Iceland",
            "(UTC+05:30)India",
            "(UTC+07:00)Indonesia",
            "(UTC+03:30)Iran",
            "(UTC+03:00)Iraq",
            "(UTC)Ireland",
            "(UTC+02:00)Israel",
            "(UTC+01:00)Italy",
            "(UTC-05:00)Jamaica",
            "(UTC+01:00)Jan Mayen",
            "(UTC+09:00)Japan" "(UTC)Jersey",
            "(UTC+02:00)Jordan",
            "(UTC+06:00)Kazakhstan",
            "(UTC+03:00)Kenya",
            "(UTC+12:00)Kiribati",
            "(UTC+09:00)Korea",
            "(UTC+01:00)Kosovo",
            "(UTC+03:00)Kuwait",
            "(UTC+06:00)Kyrgyzstan",
            "(UTC+07:00)Laos",
            "(UTC+02:00)Latvia",
            "(UTC+02:00)Lebanon",
            "(UTC+02:00)Lesotho",
            "(UTC)Liberia",
            "(UTC+02:00)Libya",
            "(UTC+01:00)Liechtenstein",
            "(UTC+02:00)Lithuania",
            "(UTC+01:00)Luxembourg",
            "(UTC+08:00)Macao SAR",
            "(UTC+01:00)Macedonia, Former Yugoslav Republic of",
            "(UTC+03:00)Madagascar",
            "(UTC+02:00)Malawi",
            "(UTC+08:00)Malaysia",
            "(UTC+05:00)Maldives",
            "(UTC)Mali",
            "(UTC+01:00)Malta",
            "(UTC)Man, Isle of",
            "(UTC+12:00)Marshall Islands",
            "(UTC-04:00)Martinique",
            "(UTC)Mauritania",
            "(UTC+04:00)Mauritius",
            "(UTC+03:00)Mayotte",
            "(UTC-06:00)Mexico",
            "(UTC+10:00)Micronesia",
            "(UTC+02:00)Moldova",
            "(UTC+01:00)Monaco",
            "(UTC+08:00)Mongolia",
            "(UTC+01:00)Montenegro",
            "(UTC-04:00)Montserrat",
            "(UTC)Morocco",
            "(UTC+02:00)Mozambique",
            "(UTC+06:30)Myanmar",
            "(UTC+01:00)Namibia",
            "(UTC+12:00)Nauru",
            "(UTC+05:45)Nepal",
            "(UTC+01:00)Netherlands",
            "(UTC+11:00)New Caledonia",
            "(UTC+12:00)New Zealand",
            "(UTC-06:00)Nicaragua",
            "(UTC+01:00)Niger",
            "(UTC+01:00)Nigeria",
            "(UTC-11:00)Niue",
            "(UTC+11:00)Norfolk Island",
            "(UTC+09:00)North Korea",
            "(UTC+10:00)Northern Mariana Islands",
            "(UTC+01:00)Norway",
            "(UTC+04:00)Oman",
            "(UTC+05:00)Pakistan",
            "(UTC+09:00)Palau",
            "(UTC+02:00)Palestinian Authority",
            "(UTC-05:00)Panama",
            "(UTC+10:00)Papua New Guinea",
            "(UTC-04:00)Paraguay",
            "(UTC-05:00)Peru",
            "(UTC+08:00)Philippines",
            "(UTC-08:00)Pitcairn Islands",
            "(UTC+01:00)Poland",
            "(UTC)Portugal",
            "(UTC-04:00)Puerto Rico",
            "(UTC+03:00)Qatar",
            "(UTC+04:00)Reunion",
            "(UTC+02:00)Romania",
            "(UTC+03:00)Russia",
            "(UTC+02:00)Rwanda",
            "(UTC-04:00)Saint Barthélemy",
            "(UTC)Saint Helena, Ascension and Tristan da Cunha",
            "(UTC-04:00)Saint Kitts and Nevis",
            "(UTC-04:00)Saint Lucia",
            "(UTC-04:00)Saint Martin (French part)",
            "(UTC-03:00)Saint Pierre and Miquelon",
            "(UTC-04:00)Saint Vincent and the Grenadines",
            "(UTC+13:00)Samoa",
            "(UTC+01:00)San Marino",
            "(UTC)São Tomé and Príncipe",
            "(UTC+03:00)Saudi Arabia",
            "(UTC)Senegal",
            "(UTC+01:00)Serbia",
            "(UTC+04:00)Seychelles",
            "(UTC)Sierra Leone",
            "(UTC+08:00)Singapore",
            "(UTC-04:00)Sint Maarten (Dutch part)",
            "(UTC+01:00)Slovakia",
            "(UTC+01:00)Slovenia",
            "(UTC+11:00)Solomon Islands" "(UTC+03:00)Somalia",
            "(UTC+02:00)South Africa",
            "(UTC-02:00)South Georgia and the South Sandwich Islands",
            "(UTC+03:00)South Sudan",
            "(UTC+01:00)Spain",
            "(UTC+05:30)Sri Lanka",
            "(UTC+03:00)Sudan",
            "(UTC-03:00)Suriname",
            "(UTC+01:00)Svalbard",
            "(UTC+02:00)Swaziland",
            "(UTC+01:00)Sweden",
            "(UTC+01:00)Switzerland",
            "(UTC+02:00)Syria",
            "(UTC+08:00)Taiwan",
            "(UTC+05:00)Tajikistan",
            "(UTC+03:00)Tanzania",
            "(UTC+07:00)Thailand",
            "(UTC)Togo",
            "(UTC+13:00)Tokelau",
            "(UTC+13:00)Tonga",
            "(UTC-04:00)Trinidad and Tobago",
            "(UTC+01:00)Tunisia",
            "(UTC+02:00)Turkey",
            "(UTC+05:00)Turkmenistan",
            "(UTC-05:00)Turks and Caicos Islands",
            "(UTC+12:00)Tuvalu",
            "(UTC-11:00)U.S. Minor Outlying Islands",
            "(UTC+03:00)Uganda",
            "(UTC+02:00)Ukraine",
            "(UTC+04:00)United Arab Emirates",
            "(UTC)United Kingdom",
            "(UTC-07:00)United States",
            "(UTC-08:00)United States",
            "(UTC-03:00)Uruguay",
            "(UTC+05:00)Uzbekistan",
            "(UTC+11:00)Vanuatu",
            "(UTC+01:00)Vatican City",
            "(UTC+07:00)Vietnam",
            "(UTC-04:00)Virgin Islands, U.S.",
            "(UTC-04:00)Virgin Islands, British",
            "(UTC+12:00)Wallis and Futuna",
            "(UTC+03:00)Yemen",
            "(UTC+02:00)Zambia",
            "(UTC+02:00)Zimbabwe",
        ]

        data_list = []
        for zone in timezone_list:
            data_list.append(
                KeyValueType(
                    key=zone.split(")")[1].replace(" ", "_").lower(),
                    label=zone,
                )
            )
        return data_list


class PropertiesType(graphene.ObjectType):
    table = graphene.Field(TablePropertiesType)
    # column = graphene.Field(ColumnPropertiesType)

    def resolve_table(self, info):
        return TablePropertiesType()


class Query(graphene.ObjectType):
    dataset = DjangoObjectField(DatasetDetailType)
    datasets = DjangoPaginatedListObjectField(
        DatasetListType,
        pagination=PageGraphqlPagination(page_size_query_param="pageSize"),
    )
    properties = graphene.Field(PropertiesType)

    def resolve_properties(self, info):
        return PropertiesType()
