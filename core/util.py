import csv
import os
import re
import uuid
from abc import ABC, abstractmethod
from datetime import datetime

import arrow
from core.models import (

    Product,

)
from django.conf import settings


def convert_to_int(string_number):
    return int("".join(string_number.split(",")))


def convert_to_float(string_number):
    return float("".join(string_number.split(",")))


def convert_to_date(month, year):
    date_formats = ("DD/MMM/YYYY", "DD/MMMM/YYYY")
    for index, f in enumerate(date_formats):
        try:
            arrow_date = arrow.get(f"01/{month}/{year}", f)
            break
        except arrow.parser.ParserMatchError:
            if index + 1 == len(date_formats):
                raise Exception(f"Cannot Parse Date 01/{month}/{year}")
    return arrow_date


def extract_dates(input):
    date_patterns = [r"^(\w+)\s(2\d+)", r"(\w+)\s*-\s*(\w+)\s*(2\d+)"]
    for p in date_patterns:
        result = re.search(p, input)
        if result:
            break
    if not result:
        raise Exception("Date Patterns did not match")

    if len(result.groups()) == 3:
        start_date = convert_to_date(result.group(1), result.group(3))
        end_date = convert_to_date(result.group(2), result.group(3))
        date_range = arrow.Arrow.range("month", start_date, end_date)
        return tuple(d.date() for d in date_range)
    elif len(result.groups()) == 2:
        return (convert_to_date(result.group(1), result.group(2)).date(),)
    else:
        raise Exception("Date format not supported")


class CsvError(Exception):
    def __init__(self, code=None, message=None):
        self.code = code
        self.message = message


class AbstractCsvValidator(ABC):
    def __init__(self, file, file_type):
        self.table = ""
        self.file = file
        self.file_type = file_type
        self.temp_file_path = None
        self.table = None

    def validate_file_type_exist(self):
        if self.file_type not in generate_download_sample_names():
            raise CsvError(
                code="FILE_TYPE_ERROR", message="Uploaded File Type does not exist"
            )

    def validate_extension(self):
        if not self.file.name.endswith(".csv"):
            raise CsvError(
                code="EXTENSION_ERROR", message="Please upload CSV file only."
            )

    def generate_table_for_validation(self):
        file_path = (
            settings.MEDIA_ROOT / "uploads" / "{0}.csv".format(str(uuid.uuid4()))
        )
        with open(file_path, "wb+") as destination:
            for chunk in self.file.chunks():
                destination.write(chunk)
        self.temp_file_path = file_path
        self.table = etl.fromcsv(file_path, encoding="utf-8-sig")

    def validate_content(self):
        problems = etl.validate(
            self.table, constraints=self.constraints(), header=self.header()
        )
        if len(problems) > 1:
            raise CsvError(code="CONTENT_ERROR", message=[err for err in problems[1:]])

    def validate(self):
        self.validate_file_type_exist()
        self.validate_extension()
        self.generate_table_for_validation()
        self.validate_content()

    def delete_file(self):
        print(str(self.temp_file_path))
        if self.temp_file_path:
            os.remove(str(self.temp_file_path))

    @abstractmethod
    def header(self):
        """
        :return:
        ('foo', 'bar', 'baz')
        """

    @abstractmethod
    def constraints(self):
        """
            :return:
        [
            dict(name='foo_int', field='foo', test=int),
            dict(name='bar_date', field='bar', test=etl.dateparser('%Y-%m-%d')),
            dict(name='baz_enum', field='baz', assertion=lambda v: v in ['Y', 'N']),
            dict(name='not_none', assertion=lambda row: None not in row),
            dict(name='qux_int', field='qux', test=int, optional=True),
        ]
        """

    def read_csv_file(self, temp_path, uploaded_file_type):
        with open(temp_path, mode="r", encoding="utf-8-sig") as csv_file:
            return list(csv.DictReader(csv_file))

    @abstractmethod
    def save_csv_to_database(self):
        pass


class FacilityStockStatus(AbstractCsvValidator):
    def header(self):
        return (
            "facility_code",
            "facility_name",
            "product_name",
            "product_code",
            "zone",
            "district",
            "period",
            "amc",
            "mos",
            "quantity",
            "status",
        )

    def constraints(self):
        return [
            dict(name="facility_code", field="facility_code", test=str),
            dict(name="facility_name", field="facility_name", test=str),
            dict(name="product_code", field="product_code", test=str),
            dict(name="product_name", field="product_name", test=str),
            dict(name="zone", field="zone", test=str),
            dict(name="district", field="district", test=str),
            dict(name="period", field="period", test=str),
            dict(name="amc", field="amc", test=str),
            dict(name="mos", field="mos", test=str),
            dict(name="status", field="status", test=str),
            dict(name="quantity", field="quantity", test=int),
        ]

    def save_csv_to_database(self, temp_path, uploaded_file_type):
        read_data = self.read_csv_file(temp_path, uploaded_file_type)
        country_object, _ = GeographicZone.objects.get_or_create(
            code="TZ", name="Tanzania", geographic_level="CNT"
        )
        for row in read_data:

            zone_object, _ = GeographicZone.objects.get_or_create(
                code=row["zone"].upper(),
                name=row["zone"],
                geographic_level="RGN",
                parent=country_object,
            )
            district_object, _ = GeographicZone.objects.get_or_create(
                code=row["district"].upper(),
                name=row["district"],
                geographic_level="DST",
                parent=zone_object,
            )

            facility_object, _ = Facility.objects.get_or_create(
                code=row["facility_code"],
                name=row["facility_name"],
                geographical_zone=district_object,
            )

            product_object, _ = Product.objects.get_or_create(
                code=row["product_code"],
                name=row["product_name"],
            )
            upload_status = UNKNOWN
            for code, name in PRODUCT_STATUS_CHOICES:
                if name.lower() == row["status"].lower():
                    upload_status = code

            valid_dates = extract_dates(row["period"])
            for d in valid_dates:
                facility_product_object, _ = FacilityProduct.objects.get_or_create(
                    facility=facility_object,
                    product=product_object,
                    period=row["period"],
                    period_date=d,
                    status=upload_status,
                    soh=convert_to_int(row["quantity"]),
                    amc=convert_to_int(row["amc"]),
                    mos=convert_to_float(row["mos"]),
                )


class VendorStockStatus(AbstractCsvValidator):
    def header(self):
        return (
            "vendor_code",
            "vendor_name",
            "product_code",
            "product_name",
            "quantity",
            "stock_date",
        )

    def constraints(self):
        return [
            dict(name="vendor_code", field="vendor_code", test=str),
            dict(name="vendor_name", field="vendor_name", test=str),
            dict(name="product_code", field="product_code", test=str),
            dict(name="product_name", field="product_name", test=str),
            dict(
                name="stock_date", field="stock_date", test=etl.dateparser("%Y-%m-%d")
            ),
            dict(name="quantity", field="quantity", test=int),
        ]

    def save_csv_to_database(self, temp_path, uploaded_file_type):
        read_data = self.read_csv_file(temp_path, uploaded_file_type)
        for row in read_data:
            vendor = Vendor.objects.filter(code=row["vendor_code"]).first()
            if not vendor:
                print("Vendor not found")
                continue

            product, _ = Product.objects.get_or_create(
                code=row["product_code"], name=row["product_name"]
            )
            VendorProduct.objects.update_or_create(
                vendor=vendor,
                product=product,
                stock_date=datetime.strptime(row["stock_date"], "%Y-%m-%d").date(),
                defaults={"quantity": row["quantity"]},
            )


UPLOAD_HANDLER = {
    # "msd_product_details": MsdProductDetailsHandler,
    # "msd_zones_forecasted_quantity": MsdForecastedQuantity,
    # "msd_zones_procurement_quantity": MsdProductProcurement,
    # "msd_zones_storage_capacity": MsdZoneStorageCapacity,
    # "forecast_tvca": ForecastTcv,
    # "procurement_tvca": ProcurementTcv
    # "supplier_stock_status": MsdSupplierStockStatus,
    "facility_stock_status": FacilityStockStatus,
    "vendor_stock_status": VendorStockStatus,
}


def generate_download_sample_names():
    return list(UPLOAD_HANDLER.keys())
