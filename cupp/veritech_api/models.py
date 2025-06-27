from django.db import models
from django.utils import timezone
from django.utils.dateparse import parse_date


def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


class General(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    employeecode = models.CharField(max_length=10, null=True, blank=True)
    originname = models.CharField(max_length=50, null=True, blank=True)
    urag = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    stateregnumber = models.CharField(max_length=50, null=True, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    employeephone = models.CharField(max_length=20, null=True, blank=True)
    postaddress = models.EmailField(null=True, blank=True)
    educationlevel = models.CharField(max_length=50, null=True, blank=True)
    maritalstatus = models.CharField(max_length=50, null=True, blank=True)
    nooffamilymember = models.IntegerField(null=True, blank=True)
    noofchildren = models.IntegerField(null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    insuredtypename = models.CharField(max_length=100, null=True, blank=True)
    statusname = models.CharField(max_length=100, null=True, blank=True)
    currentstatusname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def save_data_to_db(cls, data):
        employeeid = data.get('employeeid', None)
        if not employeeid:
            return  # Skip if no employeeid

        general_defaults = {
            'gender': data.get('gender', None),
            'employeecode': data.get('employeecode', None),
            'originname': data.get('originname', None),
            'urag': data.get('urag', None),
            'firstname': data.get('firstname', None),
            'lastname': data.get('lastname', None),
            'stateregnumber': data.get('stateregnumber', None),
            'dateofbirth': parse_date(data.get('dateofbirth', None)) if data.get('dateofbirth') else None,
            'employeephone': data.get('employeephone', None),
            'postaddress': data.get('postaddress', None),
            'educationlevel': data.get('educationlevel', None),
            'maritalstatus': data.get('maritalstatus', None),
            'nooffamilymember': safe_int(data.get('nooffamilymember', 0)),
            'noofchildren': safe_int(data.get('noofchildren', 0)),
            'departmentname': data.get('departmentname', None),
            'positionname': data.get('positionname', None),
            'insuredtypename': data.get('insuredtypename', None),
            'statusname': data.get('statusname', None),
            'currentstatusname': data.get('currentstatusname', None)
        }

        cls.objects.update_or_create(employeeid=employeeid, defaults=general_defaults)


# Address table
class Address(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    addresstypename = models.CharField(max_length=100, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    districtname = models.CharField(max_length=50, null=True, blank=True)
    streetname = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Bank table
class Bank(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    bankname = models.CharField(max_length=100, null=True, blank=True)
    bankaccountnumber = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Experience table
class Experience(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Education table
class Education(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    edutype = models.CharField(max_length=100, null=True, blank=True)
    edulevel = models.CharField(max_length=100, null=True, blank=True)
    startyearid = models.CharField(max_length=4, null=True, blank=True)
    endyearid = models.CharField(max_length=4, null=True, blank=True)
    countryname = models.CharField(max_length=50, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    schoolname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Attitude table for Punishment/Reward
class Attitude(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    punishment = models.CharField(max_length=100, null=True, blank=True)
    punishmentdate = models.DateField(null=True, blank=True)
    punishmenttypeid = models.CharField(max_length=100, null=True, blank=True)
    rewardtypename = models.CharField(max_length=100, null=True, blank=True)
    rewardname = models.CharField(max_length=100, null=True, blank=True)
    rewarddate = models.DateField(null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    rectorshipnumber = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Family table
class Family(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    relationshipname = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    workname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Skills table for language, talent, skills, hrmexam
class Skills(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    skillname = models.CharField(max_length=100, null=True, blank=True)
    examname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SubInfo(models.Model):
    employeeid = models.CharField(max_length=50, null=True, blank=True)
    workstartdate = models.DateField(null=True, blank=True)
    workenddate = models.DateField(null=True, blank=True)
    booktypename = models.CharField(max_length=255, null=True, blank=True)
    departmentcode = models.CharField(max_length=20, null=True, blank=True)
    departmentname = models.CharField(max_length=20, null=True, blank=True)
    positionname = models.CharField(max_length=50, null=True, blank=True)
    insuredtypename = models.CharField(max_length=255, null=True, blank=True)
    statusname = models.CharField(max_length=50, null=True, blank=True)


class CandidateGeneral(models.Model):
    candidateid = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=20, null=True, blank=True)
    civilregnumber = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    stateregnumber = models.CharField(max_length=20, null=True, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    departmentcode = models.CharField(max_length=20, blank=True, null=True)
    departmentname = models.CharField(max_length=50, blank=True, null=True)
    positioncode = models.CharField(max_length=20, blank=True, null=True)
    positionname = models.CharField(max_length=100, blank=True, null=True)
    phonenumber = models.IntegerField(blank=True, null=True)
    createddate = models.CharField(max_length=50, null=True, blank=True)
    workedtime = models.CharField(max_length=50, null=True, blank=True)


class CandidateAddress(models.Model):
    candidateid = models.CharField(max_length=50, blank=True, null=True)
    addresstypename = models.CharField(max_length=255, blank=True, null=True)
    cityname = models.CharField(max_length=100, blank=True, null=True)
    districtname = models.CharField(max_length=100, blank=True, null=True)
    streetname = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)


class in_Act_General(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    employeecode = models.CharField(max_length=10, null=True, blank=True)
    originname = models.CharField(max_length=50, null=True, blank=True)
    urag = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    stateregnumber = models.CharField(max_length=50, null=True, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    employeephone = models.CharField(max_length=20, null=True, blank=True)
    postaddress = models.EmailField(null=True, blank=True)
    educationlevel = models.CharField(max_length=50, null=True, blank=True)
    maritalstatus = models.CharField(max_length=50, null=True, blank=True)
    nooffamilymember = models.IntegerField(null=True, blank=True)
    noofchildren = models.IntegerField(null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    insuredtypename = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update on every save


# Address table
class in_Act_Address(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    addresstypename = models.CharField(max_length=100, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    districtname = models.CharField(max_length=50, null=True, blank=True)
    streetname = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Bank table
class in_Act_Bank(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    bankname = models.CharField(max_length=100, null=True, blank=True)
    bankaccountnumber = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Experience table
class in_Act_Experience(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Education table
class in_Act_Education(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    edutype = models.CharField(max_length=100, null=True, blank=True)
    edulevel = models.CharField(max_length=100, null=True, blank=True)
    startyearid = models.CharField(max_length=4, null=True, blank=True)
    endyearid = models.CharField(max_length=4, null=True, blank=True)
    countryname = models.CharField(max_length=50, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    schoolname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Attitude table for Punishment/Reward
class in_Act_Attitude(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    punishment = models.CharField(max_length=100, null=True, blank=True)
    punishmentdate = models.DateField(null=True, blank=True)
    punishmenttypeid = models.CharField(max_length=100, null=True, blank=True)
    rewardtypename = models.CharField(max_length=100, null=True, blank=True)
    rewardname = models.CharField(max_length=100, null=True, blank=True)
    rewarddate = models.DateField(null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    rectorshipnumber = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Family table
class in_Act_Family(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    relationshipname = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    workname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Skills table for language, talent, skills, hrmexam
class in_Act_Skills(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    skillname = models.CharField(max_length=100, null=True, blank=True)
    examname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class in_Act_SubInfo(models.Model):
    employeeid = models.CharField(max_length=50, null=True, blank=True)
    workstartdate = models.DateField(null=True, blank=True)
    workenddate = models.DateField(null=True, blank=True)
    booktypename = models.CharField(max_length=255, null=True, blank=True)
    departmentcode = models.CharField(max_length=20, null=True, blank=True)
    departmentname = models.CharField(max_length=255, null=True, blank=True)
    positionname = models.CharField(max_length=255, null=True, blank=True)
    insuredtypename = models.CharField(max_length=255, null=True, blank=True)
    statusname = models.CharField(max_length=50, null=True, blank=True)


# General table
class General_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    employeecode = models.CharField(max_length=10, null=True, blank=True)
    originname = models.CharField(max_length=50, null=True, blank=True)
    urag = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    stateregnumber = models.CharField(max_length=50, null=True, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    employeephone = models.CharField(max_length=20, null=True, blank=True)
    postaddress = models.EmailField(null=True, blank=True)
    educationlevel = models.CharField(max_length=50, null=True, blank=True)
    maritalstatus = models.CharField(max_length=50, null=True, blank=True)
    nooffamilymember = models.IntegerField(null=True, blank=True)
    noofchildren = models.IntegerField(null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    insuredtypename = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update on every save


# Address table
class Address_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    addresstypename = models.CharField(max_length=100, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    districtname = models.CharField(max_length=50, null=True, blank=True)
    streetname = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Bank table
class Bank_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    bankname = models.CharField(max_length=100, null=True, blank=True)
    bankaccountnumber = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Experience table
class Experience_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Education table
class Education_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    edutype = models.CharField(max_length=100, null=True, blank=True)
    edulevel = models.CharField(max_length=100, null=True, blank=True)
    startyearid = models.CharField(max_length=4, null=True, blank=True)
    endyearid = models.CharField(max_length=4, null=True, blank=True)
    countryname = models.CharField(max_length=50, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    schoolname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Attitude table for Punishment/Reward
class Attitude_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    punishment = models.CharField(max_length=100, null=True, blank=True)
    punishmentdate = models.DateField(null=True, blank=True)
    punishmenttypeid = models.CharField(max_length=100, null=True, blank=True)
    rewardtypename = models.CharField(max_length=100, null=True, blank=True)
    rewardname = models.CharField(max_length=100, null=True, blank=True)
    rewarddate = models.DateField(null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    rectorshipnumber = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Family table
class Family_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    relationshipname = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    workname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Skills table for language, talent, skills, hrmexam
class Skills_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    skillname = models.CharField(max_length=100, null=True, blank=True)
    examname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SubInfo_24(models.Model):
    employeeid = models.CharField(max_length=50, null=True, blank=True)
    workstartdate = models.DateField(null=True, blank=True)
    workenddate = models.DateField(null=True, blank=True)
    booktypename = models.CharField(max_length=255, null=True, blank=True)
    departmentcode = models.CharField(max_length=20, null=True, blank=True)
    departmentname = models.CharField(max_length=20, null=True, blank=True)
    positionname = models.CharField(max_length=50, null=True, blank=True)
    insuredtypename = models.CharField(max_length=255, null=True, blank=True)
    statusname = models.CharField(max_length=50, null=True, blank=True)


class CandidateGeneral_24(models.Model):
    candidateid = models.CharField(max_length=50, null=True, blank=True)
    code = models.CharField(max_length=20, null=True, blank=True)
    civilregnumber = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    stateregnumber = models.CharField(max_length=20, null=True, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    departmentcode = models.CharField(max_length=20, blank=True, null=True)
    departmentname = models.CharField(max_length=50, blank=True, null=True)
    positioncode = models.CharField(max_length=20, blank=True, null=True)
    positionname = models.CharField(max_length=100, blank=True, null=True)
    phonenumber = models.IntegerField(blank=True, null=True)
    createddate = models.CharField(max_length=50, null=True, blank=True)
    workedtime = models.CharField(max_length=50, null=True, blank=True)


class CandidateAddress_24(models.Model):
    candidateid = models.CharField(max_length=50, blank=True, null=True)
    addresstypename = models.CharField(max_length=255, blank=True, null=True)
    cityname = models.CharField(max_length=100, blank=True, null=True)
    districtname = models.CharField(max_length=100, blank=True, null=True)
    streetname = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)


class in_Act_General_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    employeecode = models.CharField(max_length=10, null=True, blank=True)
    originname = models.CharField(max_length=50, null=True, blank=True)
    urag = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    stateregnumber = models.CharField(max_length=50, null=True, blank=True)
    dateofbirth = models.DateField(null=True, blank=True)
    employeephone = models.CharField(max_length=20, null=True, blank=True)
    postaddress = models.EmailField(null=True, blank=True)
    educationlevel = models.CharField(max_length=50, null=True, blank=True)
    maritalstatus = models.CharField(max_length=50, null=True, blank=True)
    nooffamilymember = models.IntegerField(null=True, blank=True)
    noofchildren = models.IntegerField(null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    insuredtypename = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when created
    updated_at = models.DateTimeField(auto_now=True)  # Automatically update on every save


# Address table
class in_Act_Address_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    addresstypename = models.CharField(max_length=100, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    districtname = models.CharField(max_length=50, null=True, blank=True)
    streetname = models.CharField(max_length=100, null=True, blank=True)
    address = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Bank table
class in_Act_Bank_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    bankname = models.CharField(max_length=100, null=True, blank=True)
    bankaccountnumber = models.CharField(max_length=50, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Experience table
class in_Act_Experience_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    departmentname = models.CharField(max_length=100, null=True, blank=True)
    positionname = models.CharField(max_length=100, null=True, blank=True)
    startdate = models.DateField(null=True, blank=True)
    enddate = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Education table
class in_Act_Education_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    edutype = models.CharField(max_length=100, null=True, blank=True)
    edulevel = models.CharField(max_length=100, null=True, blank=True)
    startyearid = models.CharField(max_length=4, null=True, blank=True)
    endyearid = models.CharField(max_length=4, null=True, blank=True)
    countryname = models.CharField(max_length=50, null=True, blank=True)
    cityname = models.CharField(max_length=50, null=True, blank=True)
    schoolname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Attitude table for Punishment/Reward
class in_Act_Attitude_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    punishment = models.CharField(max_length=100, null=True, blank=True)
    punishmentdate = models.DateField(null=True, blank=True)
    punishmenttypeid = models.CharField(max_length=100, null=True, blank=True)
    rewardtypename = models.CharField(max_length=100, null=True, blank=True)
    rewardname = models.CharField(max_length=100, null=True, blank=True)
    rewarddate = models.DateField(null=True, blank=True)
    organizationname = models.CharField(max_length=100, null=True, blank=True)
    rectorshipnumber = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Family table
class in_Act_Family_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    relationshipname = models.CharField(max_length=50, null=True, blank=True)
    firstname = models.CharField(max_length=50, null=True, blank=True)
    lastname = models.CharField(max_length=50, null=True, blank=True)
    birthdate = models.DateField(null=True, blank=True)
    mobile = models.CharField(max_length=100, null=True, blank=True)
    workname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


# Skills table for language, talent, skills, hrmexam
class in_Act_Skills_24(models.Model):
    employeeid = models.CharField(max_length=20, null=True, blank=True)
    skillname = models.CharField(max_length=100, null=True, blank=True)
    examname = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class in_Act_SubInfo_24(models.Model):
    employeeid = models.CharField(max_length=50, null=True, blank=True)
    workstartdate = models.DateField(null=True, blank=True)
    workenddate = models.DateField(null=True, blank=True)
    booktypename = models.CharField(max_length=255, null=True, blank=True)
    departmentcode = models.CharField(max_length=20, null=True, blank=True)
    departmentname = models.CharField(max_length=255, null=True, blank=True)
    positionname = models.CharField(max_length=255, null=True, blank=True)
    insuredtypename = models.CharField(max_length=255, null=True, blank=True)
    statusname = models.CharField(max_length=50, null=True, blank=True)
