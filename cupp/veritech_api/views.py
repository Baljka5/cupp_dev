import requests
from django.utils.dateparse import parse_date
from django.shortcuts import render
from .models import General, Address, Bank, Experience, Education, Attitude, Family, Skills, SubInfo, CandidateGeneral, \
    CandidateAddress, in_Act_General, in_Act_Experience, in_Act_Bank, in_Act_Address, in_Act_Education, in_Act_Attitude, \
    in_Act_Family, in_Act_Skills, in_Act_SubInfo
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse


@csrf_exempt
def fetch_and_save_employee_data(request):
    url = "http://10.10.90.22:8080/erp-services/RestWS/runJson"
    headers = {'Content-Type': 'application/json'}

    payload = {
        "request": {
            "username": "cu_hr",
            "password": "123",
            "command": "cuHrEmpInfoDv_004",
            "parameters": {
                "criteria": {
                    "id": {
                        "0": {
                            "operator": "=",
                            "operand": "1"
                        }
                    },
                    "filterActive": {
                        "0": {
                            "operator": "=",
                            "operand": "1"
                        }
                    }

                }
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()['response']['result']
        # Save data for the first 60 employees (or fewer if not available)
        employee_data = data.get('empinfo', {})
        save_multiple_employees(employee_data)
        return HttpResponse("Data saved successfully.", status=200)
    else:
        return HttpResponse("Failed to fetch data from external service.", status=500)


@csrf_exempt
def fetch_and_save_inactive_employee_data(request):
    url = "http://10.10.90.22:8080/erp-services/RestWS/runJson"
    headers = {'Content-Type': 'application/json'}

    payload = {
        "request": {
            "username": "cu_hr",
            "password": "123",
            "command": "cuHrEmpInfoDv_004",
            "parameters": {
                "criteria": {
                    "id": {
                        "0": {
                            "operator": "=",
                            "operand": "1"
                        }
                    },
                    "filterActive": {
                        "0": {
                            "operator": "=",
                            "operand": "0"
                        }
                    }

                }
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        data = response.json()['response']['result']
        # Save data for the first 60 employees (or fewer if not available)
        in_act_employee_data = data.get('empinfo', {})
        save_multiple_inactive_employees(in_act_employee_data)
        return HttpResponse("Data saved successfully.", status=200)
    else:
        return HttpResponse("Failed to fetch data from external service.", status=500)


@csrf_exempt
def fetch_and_save_candidate_employee_data(request):
    url = "http://10.10.90.22:8080/erp-services/RestWS/runJson"
    headers = {'Content-Type': 'application/json'}

    payload = {
        "request": {
            "username": "cu_hr",
            "password": "123",
            "command": "cuHrCandidateInfoDv_004",
            "parameters": {
                "criteria": {
                    "id": {
                        "0": {
                            "operator": "=",
                            "operand": "1"
                        }
                    }
                }
            }
        }
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        candidate_data = response.json()['response']['result']
        employee_candidate_data = candidate_data.get('candidateinfo', {})
        save_multiple_candidate_employees(employee_candidate_data)
        return HttpResponse("Data saved successfully.", status=200)
    else:
        return HttpResponse("Failed to fetch data from external service.", status=500)


def save_multiple_candidate_employees(candidate_employee_data):
    """
    Save data for the first 60 employees (or fewer if not available), ensuring no duplicates.
    """
    for idx, candidate_employee in enumerate(candidate_employee_data.values()):
        if idx >= 5000:
            break
        # Check if employee with the same employeeid already exists to avoid duplication
        if not CandidateGeneral.objects.filter(candidateid=candidate_employee.get('candidateid')).exists():
            save_candidate_data_to_db(candidate_employee)


def save_multiple_employees(employee_data):
    """
    Save data for the first 60 employees (or fewer if not available), ensuring no duplicates.
    """
    for idx, employee in enumerate(employee_data.values()):
        if idx >= 5000:
            break
        # Check if employee with the same employeeid already exists to avoid duplication
        if not General.objects.filter(employeeid=employee.get('employeeid')).exists():
            save_data_to_db(employee)


def save_multiple_inactive_employees(employee_data):
    """
    Save data for the first 60 employees (or fewer if not available), ensuring no duplicates.
    """
    for idx, employee in enumerate(employee_data.values()):
        if idx >= 5000:
            break
        # Check if employee with the same employeeid already exists to avoid duplication
        if not in_Act_General.objects.filter(employeeid=employee.get('employeeid')).exists():
            save_inactive_data_to_db(employee)


def safe_int(value):
    """
    Helper function to safely convert a value to int.
    Returns 0 if the value is None or an empty string.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0


def save_data_to_db(data):
    # Save General Data
    general_info = General(
        employeeid=data.get('employeeid', None),
        gender=data.get('gender', None),
        employeecode=data.get('employeecode', None),
        originname=data.get('originname', None),
        urag=data.get('urag', None),
        firstname=data.get('firstname', None),
        lastname=data.get('lastname', None),
        stateregnumber=data.get('stateregnumber', None),
        dateofbirth=parse_date_if_valid(data.get('dateofbirth', None)),
        employeephone=data.get('employeephone', None),
        postaddress=data.get('postaddress', None),
        educationlevel=data.get('educationlevel', None),
        maritalstatus=data.get('maritalstatus', None),
        nooffamilymember=safe_int(data.get('nooffamilymember', 0)),
        noofchildren=safe_int(data.get('noofchildren', 0)),
        departmentname=data.get('departmentname', None),
        positionname=data.get('positionname', None),
        insuredtypename=data.get('insuredtypename', None)
    )
    general_info.save()

    # Save Address Data
    for i in range(safe_int(data.get('empaddress_size', 0))):  # Use safe_int to handle missing/empty keys
        address = data['empaddress'].get(str(i), {})
        address_record = Address(
            employeeid=address.get('employeeid', None),
            addresstypename=address.get('addresstypename', None),
            cityname=address.get('cityname', None),
            districtname=address.get('districtname', None),
            streetname=address.get('streetname', None),
            address=address.get('address', None)
        )
        address_record.save()

    # Save Bank Data
    for i in range(safe_int(data.get('empbank_size', 0))):
        bank = data['empbank'].get(str(i), {})
        bank_record = Bank(
            employeeid=bank.get('employeeid', None),
            bankname=bank.get('bankname', None),
            bankaccountnumber=bank.get('bankaccountnumber', None)
        )
        bank_record.save()

    # Save Experience Data
    for i in range(safe_int(data.get('empworkexp_size', 0))):
        experience = data['empworkexp'].get(str(i), {})
        experience_record = Experience(
            employeeid=experience.get('employeeid', None),
            organizationname=experience.get('organizationname', None),
            departmentname=experience.get('departmentname', None),
            positionname=experience.get('positionname', None),
            startdate=parse_date_if_valid(experience.get('startdate', None)),
            enddate=parse_date_if_valid(experience.get('enddate', None))
        )
        experience_record.save()

    # Save Education Data
    for i in range(safe_int(data.get('empeducation_size', 0))):
        education = data['empeducation'].get(str(i), {})
        education_record = Education(
            employeeid=education.get('employeeid', None),
            edutype=education.get('edutype', None),
            edulevel=education.get('edulevel', None),
            startyearid=education.get('startyearid', None),
            endyearid=education.get('endyearid', None),
            countryname=education.get('countryname', None),
            cityname=education.get('cityname', None),
            schoolname=education.get('schoolname', None)
        )
        education_record.save()

    # Save Attitude Data (Punishment and Reward)
    for i in range(safe_int(data.get('emppunishment_size', 0))):
        punishment = data['emppunishment'].get(str(i), {})
        attitude_record = Attitude(
            employeeid=punishment.get('employeeid', None),
            punishment=punishment.get('punishment', None),
            punishmentdate=parse_date_if_valid(punishment.get('punishmentdate', None)),
            punishmenttypeid=punishment.get('punishmenttypeid', None),
            rectorshipnumber=punishment.get('rectorshipnumber', None)
        )
        attitude_record.save()

    for i in range(safe_int(data.get('empreward_size', 0))):
        reward = data['empreward'].get(str(i), {})
        attitude_record = Attitude(
            employeeid=reward.get('employeeid', None),
            rewardtypename=reward.get('rewardtypename', None),
            rewardname=reward.get('rewardname', None),
            rewarddate=parse_date_if_valid(reward.get('rewarddate', None)),
            organizationname=reward.get('organizationname', None)
        )
        attitude_record.save()

    # Save Family Data
    for i in range(safe_int(data.get('empfamily_size', 0))):
        family = data['empfamily'].get(str(i), {})
        family_record = Family(
            employeeid=family.get('employeeid', None),
            relationshipname=family.get('relationshipname', None),
            firstname=family.get('firstname', None),
            lastname=family.get('lastname', None),
            birthdate=parse_date_if_valid(family.get('birthdate', None)),
            mobile=family.get('mobile', None),
            workname=family.get('workname', None)
        )
        family_record.save()

    # Save Skills Data (Language, Talent, Skills, Hrmexam)
    for i in range(safe_int(data.get('emplanguage_size', 0))):
        language = data['emplanguage'].get(str(i), {})
        skills_record = Skills(
            employeeid=language.get('employeeid', None),
            skillname=language.get('skillname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('emptalent_size', 0))):
        talent = data['emptalent'].get(str(i), {})
        skills_record = Skills(
            employeeid=talent.get('employeeid', None),
            skillname=talent.get('skillname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('empskill_size', 0))):
        skill = data['empskill'].get(str(i), {})
        skills_record = Skills(
            employeeid=skill.get('employeeid', None),
            skillname=skill.get('skillname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('hrmexam_size', 0))):
        exam = data['hrmexam'].get(str(i), {})
        skills_record = Skills(
            employeeid=exam.get('employeeid', None),
            examname=exam.get('examname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('empsubinfo_size', 0))):
        subinfo = data['empsubinfo'].get(str(i), {})
        subinfo_record = SubInfo(
            employeeid=subinfo.get('employeeid', None),
            workstartdate=parse_date_if_valid(subinfo.get('workstartdate', None)),
            workenddate=parse_date_if_valid(subinfo.get('workenddate', None)),
            booktypename=subinfo.get('booktypename', None),
            departmentcode=subinfo.get('departmentcode', None),
            departmentname=subinfo.get('departmentname', None),
            positionname=subinfo.get('positionname', None),
            insuredtypename=subinfo.get('insuredtypename', None),
            statusname=subinfo.get('statusname', None)
        )
        subinfo_record.save()


def save_inactive_data_to_db(data):
    # Save General Data
    general_info = in_Act_General(
        employeeid=data.get('employeeid', None),
        gender=data.get('gender', None),
        employeecode=data.get('employeecode', None),
        originname=data.get('originname', None),
        urag=data.get('urag', None),
        firstname=data.get('firstname', None),
        lastname=data.get('lastname', None),
        stateregnumber=data.get('stateregnumber', None),
        dateofbirth=parse_date_if_valid(data.get('dateofbirth', None)),
        employeephone=data.get('employeephone', None),
        postaddress=data.get('postaddress', None),
        educationlevel=data.get('educationlevel', None),
        maritalstatus=data.get('maritalstatus', None),
        nooffamilymember=safe_int(data.get('nooffamilymember', 0)),
        noofchildren=safe_int(data.get('noofchildren', 0)),
        departmentname=data.get('departmentname', None),
        positionname=data.get('positionname', None),
        insuredtypename=data.get('insuredtypename', None)
    )
    general_info.save()

    # Save Address Data
    for i in range(safe_int(data.get('empaddress_size', 0))):  # Use safe_int to handle missing/empty keys
        address = data['empaddress'].get(str(i), {})
        address_record = in_Act_Address(
            employeeid=address.get('employeeid', None),
            addresstypename=address.get('addresstypename', None),
            cityname=address.get('cityname', None),
            districtname=address.get('districtname', None),
            streetname=address.get('streetname', None),
            address=address.get('address', None)
        )
        address_record.save()

    # Save Bank Data
    for i in range(safe_int(data.get('empbank_size', 0))):
        bank = data['empbank'].get(str(i), {})
        bank_record = in_Act_Bank(
            employeeid=bank.get('employeeid', None),
            bankname=bank.get('bankname', None),
            bankaccountnumber=bank.get('bankaccountnumber', None)
        )
        bank_record.save()

    # Save Experience Data
    for i in range(safe_int(data.get('empworkexp_size', 0))):
        experience = data['empworkexp'].get(str(i), {})
        experience_record = in_Act_Experience(
            employeeid=experience.get('employeeid', None),
            organizationname=experience.get('organizationname', None),
            departmentname=experience.get('departmentname', None),
            positionname=experience.get('positionname', None),
            startdate=parse_date_if_valid(experience.get('startdate', None)),
            enddate=parse_date_if_valid(experience.get('enddate', None))
        )
        experience_record.save()

    # Save Education Data
    for i in range(safe_int(data.get('empeducation_size', 0))):
        education = data['empeducation'].get(str(i), {})
        education_record = in_Act_Education(
            employeeid=education.get('employeeid', None),
            edutype=education.get('edutype', None),
            edulevel=education.get('edulevel', None),
            startyearid=education.get('startyearid', None),
            endyearid=education.get('endyearid', None),
            countryname=education.get('countryname', None),
            cityname=education.get('cityname', None),
            schoolname=education.get('schoolname', None)
        )
        education_record.save()

    # Save Attitude Data (Punishment and Reward)
    for i in range(safe_int(data.get('emppunishment_size', 0))):
        punishment = data['emppunishment'].get(str(i), {})
        attitude_record = in_Act_Attitude(
            employeeid=punishment.get('employeeid', None),
            punishment=punishment.get('punishment', None),
            punishmentdate=parse_date_if_valid(punishment.get('punishmentdate', None)),
            punishmenttypeid=punishment.get('punishmenttypeid', None),
            rectorshipnumber=punishment.get('rectorshipnumber', None)
        )
        attitude_record.save()

    for i in range(safe_int(data.get('empreward_size', 0))):
        reward = data['empreward'].get(str(i), {})
        attitude_record = in_Act_Attitude(
            employeeid=reward.get('employeeid', None),
            rewardtypename=reward.get('rewardtypename', None),
            rewardname=reward.get('rewardname', None),
            rewarddate=parse_date_if_valid(reward.get('rewarddate', None)),
            organizationname=reward.get('organizationname', None)
        )
        attitude_record.save()

    # Save Family Data
    for i in range(safe_int(data.get('empfamily_size', 0))):
        family = data['empfamily'].get(str(i), {})
        family_record = in_Act_Family(
            employeeid=family.get('employeeid', None),
            relationshipname=family.get('relationshipname', None),
            firstname=family.get('firstname', None),
            lastname=family.get('lastname', None),
            birthdate=parse_date_if_valid(family.get('birthdate', None)),
            mobile=family.get('mobile', None),
            workname=family.get('workname', None)
        )
        family_record.save()

    # Save Skills Data (Language, Talent, Skills, Hrmexam)
    for i in range(safe_int(data.get('emplanguage_size', 0))):
        language = data['emplanguage'].get(str(i), {})
        skills_record = in_Act_Skills(
            employeeid=language.get('employeeid', None),
            skillname=language.get('skillname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('emptalent_size', 0))):
        talent = data['emptalent'].get(str(i), {})
        skills_record = in_Act_Skills(
            employeeid=talent.get('employeeid', None),
            skillname=talent.get('skillname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('empskill_size', 0))):
        skill = data['empskill'].get(str(i), {})
        skills_record = in_Act_Skills(
            employeeid=skill.get('employeeid', None),
            skillname=skill.get('skillname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('hrmexam_size', 0))):
        exam = data['hrmexam'].get(str(i), {})
        skills_record = in_Act_Skills(
            employeeid=exam.get('employeeid', None),
            examname=exam.get('examname', None)
        )
        skills_record.save()

    for i in range(safe_int(data.get('empsubinfo_size', 0))):
        subinfo = data['empsubinfo'].get(str(i), {})
        subinfo_record = in_Act_SubInfo(
            employeeid=subinfo.get('employeeid', None),
            workstartdate=parse_date_if_valid(subinfo.get('workstartdate', None)),
            workenddate=parse_date_if_valid(subinfo.get('workenddate', None)),
            booktypename=subinfo.get('booktypename', None),
            departmentcode=subinfo.get('departmentcode', None),
            departmentname=subinfo.get('departmentname', None),
            positionname=subinfo.get('positionname', None),
            insuredtypename=subinfo.get('insuredtypename', None),
            statusname=subinfo.get('statusname', None)
        )
        subinfo_record.save()


def save_candidate_data_to_db(candidate_data):
    # Save General Data
    candidate_general_info = CandidateGeneral(
        candidateid=candidate_data.get('candidateid', None),
        code=candidate_data.get('code', None),
        civilregnumber=candidate_data.get('civilregnumber', None),
        firstname=candidate_data.get('firstname', None),
        lastname=candidate_data.get('lastname', None),
        stateregnumber=candidate_data.get('stateregnumber', None),
        dateofbirth=parse_date_if_valid(candidate_data.get('dateofbirth', None)),
        departmentcode=candidate_data.get('departmentcode', None),
        departmentname=candidate_data.get('departmentname', None),
        positionname=candidate_data.get('positionname', None),
        phonenumber=candidate_data.get('phonenumber', None),
        createddate=candidate_data.get('createddate', None),
        workedtime=candidate_data.get('workedtime', None),
    )
    candidate_general_info.save()

    for i in range(
            safe_int(candidate_data.get('candidateaddress_size', 0))):  # Use safe_int to handle missing/empty keys
        candidate_address = candidate_data['candidateaddress'].get(str(i), {})
        candidate_address_record = CandidateAddress(
            candidateid=candidate_address.get('candidateid', None),
            addresstypename=candidate_address.get('addresstypename', None),
            cityname=candidate_address.get('cityname', None),
            districtname=candidate_address.get('districtname', None),
            streetname=candidate_address.get('streetname', None),
            address=candidate_address.get('address', None)
        )
        candidate_address_record.save()


def parse_date_if_valid(date_string):
    if date_string:
        return parse_date(date_string)
    return None
