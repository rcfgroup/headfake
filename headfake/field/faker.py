import attr

from .core import FakerField


@attr.s(kw_only=True)
class NameField(FakerField):
    """
    Base for a name field which uses faker to generate. The supplied 'gender_field' points to the field in the fieldset
    which generates the gender value. It uses this field and row value to determine whether the generated name is male
    or female.
    """
    gender_field = attr.ib()

    def init_from_fieldset(self, fieldset):
        self.gender = fieldset.field_map.get(self.gender_field)

    def _next_value(self, row):
        if row.get(self.gender_field) == self.gender.male_value:
            return self._male_name()
        if row.get(self.gender_field) == self.gender.female_value:
            return self._female_name()


@attr.s(kw_only=True)
class TimeField(FakerField):
    """
    Create mock time using faker
    """
    format = attr.ib("%H:%M")

    def _next_value(self, row):
        return self._fake.time(pattern=self.format)


class FirstNameField(NameField):
    """
    Generate first name based on gender using the faker module (see NameField).
    """

    def _male_name(self):
        return self._fake.first_name_male()

    def _female_name(self):
        return self._fake.first_name_female()


class LastNameField(NameField):
    """
    Generate last name using the faker module.
    """

    def _male_name(self):
        return self._fake.last_name_male()

    def _female_name(self):
        return self._fake.last_name_female()


@attr.s(kw_only=True)
class MiddleNameField(NameField):
    """
    Mock middle name field.
    """

    first_name_field = attr.ib()

    def _male_name(self):
        return self._fake.first_name_male()

    def _female_name(self):
        return self._fake.first_name_female()

    def next_value(self, row):
        val = super().next_value(row)
        if val == "":
            return val
        if val == row.get(self.first_name_field):
            return self.next_value(row)

        return val


@attr.s
class AddressField(FakerField):
    """
    Mock address line field.
    """

    line_no = attr.ib()

    def _next_value(self, row):
        if self.line_no == 1:
            return self._fake.street_address()

        if self.line_no == 2:
            return self._fake.secondary_address()

        if self.line_no == 3:
            return self._fake.city()

        if self.line_no == 4:
            return ""


@attr.s(kw_only=True)
class PostcodeField(FakerField):
    """
    Mock postcode field.
    """

    def _next_value(self, row):
        return self._fake.postcode()


@attr.s(kw_only=True)
class PhoneField(FakerField):
    """
    Mock phone number field.
    """

    type = attr.ib(default='default')

    def _next_value(self, row):
        if self.type in ['cell', 'mobile']:
            return self._fake.cellphone_number()
        else:
            return self._fake.phone_number()


@attr.s(kw_only=True)
class EmailField(FakerField):
    """
    Create mock email using faker
    """
    safe = attr.ib(True)

    def _next_value(self, row):
        if self.safe:
            return self._fake.safe_email()
        else:
            return self._fake.email()


@attr.s(kw_only=True)
class PasswordField(FakerField):
    """
    Create mock password using faker
    """
    length = attr.ib(16)
    special_chars = attr.ib(True)
    digits = attr.ib(True)
    upper_case = attr.ib(True)
    lower_case = attr.ib(True)

    def _next_value(self, row):
        return self._fake.password(
            length=self.length,
            special_chars=self.special_chars,
            digits=self.digits,
            upper_case=self.upper_case,
            lower_case=self.lower_case
        )


@attr.s(kw_only=True)
class TextField(FakerField):
    """
    Generate  text using the faker.lorem provider. 'max_length' controls how long the text is allowed to be.
    """
    max_length: int = attr.ib(default=50)

    def _next_value(self, row):
        return self._fake.text(max_nb_chars=self.max_length)


@attr.s(kw_only=True)
class MemoField(FakerField):
    """
    Generate paragraphs using the faker.lorem provider. 'sentences' controls the exact number of sentences, when 'exact' is
    set to True, when set to False it will return a variable number of sentences (never less than 1) +- 40% of the
    'sentences' parameter.
    """
    sentences: int = attr.ib(default=3)
    exact: bool = attr.ib(default=False)

    def _next_value(self, row):
        return self._fake.paragraph(nb_sentences=self.sentences,
                                    variable_nb_sentences=not self.exact)
