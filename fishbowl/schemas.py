from marshmallow import Schema, fields, validate, validates_schema, ValidationError
from marshmallow.decorators import validates_schema


# Double quotes in the text value must be doubled to import properly

# TODO
#  Text - A textual value.
#        If it contains a line break, comma or double quote, it must be wrapped with double quotes on both ends. 
#        If a field is wrapped, all text must be inside the double quotes.
#        Double quotes in the text value must be doubled to import properly 

# Numeric - A decimal number greater than or equal to zero with up to four digits after the decimal point.
#           The number must not have thousands' separators in it or dollar signs - 1234.56 is a valid number, while $1,234.56 is not. 



class SalesOrder(Schema):
    flag = fields.String(required=True, validate=validate.OneOf(["SO"]))
    number = fields.String(required=True, validate=validate.Length(max=25))
    status = fields.Integer(
        requied=True, validate=validate.OneOf([10, 20, 95])
    )  # TODO: Probably more this is from docs
    customer_name = fields.String(required=True, validate=validate.Length(max=40))
    customer_contact = fields.String(validate=validate.Length(max=30))
    bill_to_name = fields.String(required=True, validate=validate.Length(max=60))
    bill_to_address = fields.String(required=True, validate=validate.Length(max=90))
    bill_to_city = fields.String(required=True, validate=validate.Length(max=30))
    bill_to_state = fields.String(required=True, validate=validate.Length(max=2))
    bill_to_zip = fields.String(required=True, validate=validate.Length(max=10))
    bill_to_country = fields.String(required=True, validate=validate.Length(max=30))
    ship_to_name = fields.String(required=True, validate=validate.Length(max=60))
    ship_to_address = fields.String(required=True, validate=validate.Length(max=90))
    ship_to_city = fields.String(required=True, validate=validate.Length(max=30))
    ship_to_state = fields.String(required=True, validate=validate.Length(max=2))
    ship_to_zip = fields.String(required=True, validate=validate.Length(max=10))
    ship_to_country = fields.String(required=True, validate=validate.Length(max=30))
    ship_to_resedential = fields.String(required=True, validate=validate.OneOf("true", "false"))
    carrier_name = fields.String(required=True, validate=validate.Length(max=30))
    tax_rate_name = fields.String(required=True, validate=validate.Length(max=31))
    priority_id = fields.Integer(validate=validate.OneOf(10, 20, 30, 40, 50))
    # TODO: Test if valid: If any of the following items are to be included, then all preceding items must be included. 
    po_number = fields.Number(validate=validate.Length(max=15))
    vendoer_po_number = fields.String(validate.Length(max=25))
    date = fields.String()
    salesman = fields.String(validate.Length(max=15))
    shipping_terms = fields.String(validate.Length(max=30))
    payment_terms = fields.String(validate.Length(max=60))
    fob = fields.String(validate.Length(max=15))
    note = fields.String()
    quickbooks_class_name = fields.String(validate.Length(max=30))
    location_group_name = fields.String(validate.Length(max=30))
    order_date_scheduled = fields.String()
    url = fields.String()
    carrier_service = fields.String()
    currency_name = fields.String(validate.Length(max=255))
    currency_rate = ""
    price_is_home_currency = fields.String())
    date_expired = fields.String()
    phone = fields.String(validate.Length(max=256))
    email = fields.String(validate.Length(max=256))
    category = fields.String(validate.Length(max=128))


class SalesOrderItem(Schema):
    flag = fields.String(required=True, validate=validate.OneOf(["Item"]))
    so_item_type_id = fields.Number(required=True, validate=validate.OneOf(10,11,12,20,21,30,31,40,50,60,70,80,90,100))
    product_number = fields.String(validate.Length(max=60))
    product_description = fields.String(validate.Length(max=256))
    product_quantity = fields.Number()
    uom = fields.String()
    product_price = fields.Number()
    taxable = fields.String()
    tax_code = fields.String()
    note = fields.String()
    item_quick_books_class_name = fields.String(validate.Length(max=30))
    item_date_scheduled = fields.String()
    show_item = fields.String()
    kit_item = fields.String(validate=validate.OneOf("true", "false"))
    fields.String(validate.Length(max=15))
    customer_part_number = fields.String()

    @validates_schema
    def validate_subtotal_and_discount(self):
        # Subtotal, Discount Percentage or Discount Amount do not require any of the values that other sales order items require
        # Subtotals do not require any other values to be specified except for the word "Subtotal" in the 'Product Number' column

        # Discounts and Assoc. Prices require the name of the discount/assoc
        # price to be specified in the "Product Number" column
        
        # BOM Configuration Items are raw goods for the line above it.


        # Notes are specified in the "Product Number" column. 

