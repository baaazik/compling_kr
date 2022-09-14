#encoding "utf-8"
//если имя человека стоит в начале предложения,
// то в файл записывается начало имени с маленькой буквы
PersonName -> Word<kwtype = "ФИО">;
Person -> PersonName interp (Person.Name);
