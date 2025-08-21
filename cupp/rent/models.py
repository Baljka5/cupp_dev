from django.db import models
from cupp.store_trainer.models import StoreTrainer
from cupp.constants import CONTRACT_TYPE_CHOICES
from django.core.validators import RegexValidator


# Create your models here.


class StrRent(models.Model):
    five_digit_validator = RegexValidator(r'^\d{5}$', 'Store number must be a 5-digit number')
    store_id = models.CharField(max_length=5, validators=[five_digit_validator], null=True, blank=True)
    str_name = models.CharField('Салбарын нэр', null=True, max_length=200)
    str_address = models.CharField('Албан ёсны хаяг', null=True, max_length=200)
    lesser1 = models.CharField('Түрээслүүлэгч 1', null=True, max_length=100)
    lesser2 = models.CharField('Түрээслүүлэгч 2', null=True, max_length=100, blank=True)
    lesser3 = models.CharField('Түрээслүүлэгч 3', blank=True, null=True, max_length=100)
    phone_number1 = models.IntegerField('Холбоо барих утас 1', null=True, default=0)
    phone_number2 = models.IntegerField('Холбоо барих утас 2', null=True, default=0, blank=True)
    phone_number3 = models.IntegerField('Холбоо барих утас 3', blank=True, null=True, default=0)
    email = models.EmailField('И-майл хаяг', null=True)
    area_size = models.IntegerField('Талбайн нийт хэмжээ м.кв', null=True)
    cont_type = models.CharField('Contract Type', max_length=10, choices=CONTRACT_TYPE_CHOICES, null=True, blank=True)
    cntr_num1 = models.CharField('Гэрээний дугаар 1', null=True, max_length=30)
    cntr_num2 = models.CharField('Гэрээний дугаар 2', blank=True, null=True, max_length=30)
    cntr_num3 = models.CharField('Гэрээний дугаар 3', blank=True, null=True, max_length=30)
    st_dt = models.DateField('Гэрээ эхлэх хугацаа', null=True)
    ed_dt = models.DateField('Дуусах хугацаа ', null=True)
    ext_ed_dt = models.DateField('Сунгагдсан хугацаа', null=True)
    hand_over_dt = models.DateField('Талбай хүлээлцсэн актын өдөр', null=True)
    rent_mo_fee = models.IntegerField('Түрээсийн төлбөр ', null=True, default=0)
    rent_mo_fee_annex1 = models.IntegerField('Түрээсийн төлбөр 12', null=True, default=0, blank=True)
    rent_mo_fee_annex2 = models.IntegerField('Түрээсийн төлбөр 2', blank=True, null=True, default=0)
    rent_mo_fee_annex3 = models.IntegerField('Түрээсийн төлбөр 3', blank=True, null=True, default=0)
    deposit_amount = models.IntegerField('Барьцаа төлбөр', null=True, default=0)
    association_no = models.CharField('СӨХ гэрээний дугаар ', null=True, max_length=30)
    association_fee = models.IntegerField('СӨХ-ийн төлбөр', null=True, default=0)
    manage_cnt_no = models.CharField('Менежемент гэрээний дугаар', null=True, max_length=30)
    manage_fee = models.IntegerField('Менежментийн төлбөр', null=True, default=0)
    exp_inc = models.CharField('Гэрээнд орсон зардал', null=True, max_length=30)
    other_cnt = models.CharField('Бусад орлого болон зардлын гэрээ', null=True, max_length=30, blank=True)
    stora_yn = models.BooleanField('Stora box', null=True)
    stora_fee = models.IntegerField('Stora box түрээсийн төлбөр', null=True, default=0)
    atm_yn = models.BooleanField('ATM', null=True)
    atm_fee = models.IntegerField('ATM түрээсийн төлбөр', null=True, default=0)
    sublet_yn = models.BooleanField('Дамжуулан түрээслэх боломжтой эсэх', null=True)
    sublet1_cnt_no = models.CharField('1 Дамжуулан түрээсийн гэрээний дугаар', null=True, max_length=30, blank=True)
    sublet1_size = models.IntegerField('1 Дамжуулан түрээсийн талбай хэмжээ', null=True, default=0, blank=True)
    sublet1_rent = models.IntegerField('1 Дамжуулан түрээсийн үнэ ', null=True, default=0, blank=True)
    sublet1_deposit = models.IntegerField('1 Дамжуулан түрээсийн барьцаа төлбөр', null=True, default=0, blank=True)
    sublet2_cnt_no = models.CharField('2 Дамжуулан түрээсийн гэрээний дугаар', blank=True, null=True, max_length=30)
    sublet2_size = models.IntegerField('2 Дамжуулан түрээсийн талбай хэмжээ', blank=True, null=True, default=0)
    sublet2_rent = models.IntegerField('2 Дамжуулан түрээсийн үнэ', blank=True, null=True, default=0)
    sublet2_deposit = models.IntegerField('2 Дамжуулан түрээсийн барьцаа төлбөр', blank=True, null=True, default=0)
    sublet3_cnt_no = models.CharField('3 Дамжуулан түрээсийн гэрээний дугаар', blank=True, null=True, max_length=30)
    sublet3_size = models.IntegerField('3 Дамжуулан түрээсийн талбай хэмжээ', blank=True, null=True, default=0)
    sublet3_rent = models.IntegerField('3 Дамжуулан түрээсийн үнэ', blank=True, null=True, default=0)
    sublet3_deposit = models.IntegerField('3 Дамжуулан түрээсийн барьцаа төлбөр', blank=True, null=True, default=0)
    letter = models.CharField('Албан бичиг', blank=True, null=True, max_length=30)
    notice = models.CharField('Өргөдөл', blank=True, null=True, max_length=200)
    other_cont = models.CharField('Бусад гэрээ', blank=True, null=True, max_length=200)
    franchise_yn = models.BooleanField('Франчайз санал болгох заалттай', null=True)
    fr_rent_yn = models.BooleanField('Дамжуулан түрээсийн заалт', null=True)
    dedication = models.CharField('Үл хөдлөх хөрөнгийн зориулалт', null=True, blank=True, max_length=100)
    notariat_yn = models.BooleanField('Нотариат', null=True)
    real_estate_yn = models.BooleanField('ҮХХ-н гэрчилгээтэй эсэх', null=True)
    special_terms = models.CharField('Гэрээний онцгой нөхцөл', blank=True, null=True, max_length=30)
    cont_resp_term = models.CharField('Гэрээний хариуцлагын заалт', null=True, max_length=50)
    cont_link = models.CharField('Гэрээний холбоос', null=True, max_length=50)

    def __str__(self):
        return self.store_id

    class Meta:
        db_table = 'str_rent'
        verbose_name = 'Rent'
