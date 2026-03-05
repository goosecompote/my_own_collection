# Ansible Collection - my_own_namespace.yandex_cloud_elk

Documentation for the collection.

## Состав  
## Модуль  
my_own_module  
создаёт или обновляет текстовый файл на хосте  
## Параметры:  
path: обязательный абсолютный путь к файлу  
content: обязательное содержимое файла  
mode: опционально права в виде строки, например 0644  
## Роль  
my_own_role  
вызывает my_own_module  
defaults  
my_own_module_path  
my_own_module_content  
my_own_module_mode  
## Пример использования модуля  
- name: Create file  
  my_own_namespace.yandex_cloud_elk.my_own_module:  
    path: /tmp/example.txt  
    content: "hello\n"  
## Пример использования роли  
- name: Use role  
  hosts: localhost  
  gather_facts: false  
  collections:  
    - my_own_namespace.yandex_cloud_elk  
  roles:  
    - role: my_own_role  
      vars:  
        my_own_module_path: /tmp/from_role.txt  
        my_own_module_content: "from role\n"  
        my_own_module_mode: null  