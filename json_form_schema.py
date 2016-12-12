import json

jsontxt1 = '''
{"name": "calculate", "title": "calculate_test", "sms_keyword": "calculate_test", "default_language": "default", "id_string": "calculate_test", "type": "survey", "children": [{"bind": {"calculate": "2+2"}, "type": "calculate", "name": "calculate_test"}, {"type": "note", "name": "calculate_test_output", "label": "2+2 = ${calculate_test}"}, {"bind": {"calculate": "if(${calculate_test_output}=${calculate_test_output}, 'success', 'error')"}, "type": "calculate", "name": "calculate_test_2"}, {"type": "note", "name": "calculate_test_2_output", "label": "${calculate_test_2}"}, {"control": {"bodyless": true}, "type": "group", "name": "meta", "children": [{"bind": {"readonly": "true()", "calculate": "concat('uuid:', uuid())"}, "type": "calculate", "name": "instanceID"}]}]}
'''

jsontxt2 = '''
{"name": "table-list", "title": "table-list", "sms_keyword": "table-list", "default_language": "default", "id_string": "table-list", "type": "survey", "children": [{"type": "note", "name": "intro", "label": "Table-list tests"}, {"control": {"appearance": "field-list"}, "name": "table_list_test2", "type": "group", "children": [{"hint": "This is a user-defined hint for the 1st row", "type": "note", "name": "generated_table_list_label_3", "label": "Table (made with an easier method)"}, {"control": {"appearance": "label"}, "type": "select one", "name": "reserved_name_for_field_list_labels_4", "choices": [{"name": "yes", "label": "Yes"}, {"name": "no", "label": "No"}]}, {"control": {"appearance": "list-nolabel"}, "name": "table_list_3", "hint": "This is a user-defined hint for the 2nd row", "choices": [{"name": "yes", "label": "Yes"}, {"name": "no", "label": "No"}], "label": "Q1", "type": "select one"}, {"control": {"appearance": "list-nolabel"}, "name": "table_list_4", "hint": "This is a user-defined hint for the 3rd row", "choices": [{"name": "yes", "label": "Yes"}, {"name": "no", "label": "No"}], "label": "Question 2", "type": "select one"}]}, {"control": {"appearance": "field-list"}, "name": "happy_sad_table", "type": "group", "children": [{"hint": "This is a user-defined hint for the 1st row", "type": "note", "name": "generated_table_list_label_7", "label": "Table with image labels (made using an easier method)"}, {"control": {"appearance": "label"}, "type": "select all that apply", "name": "reserved_name_for_field_list_labels_8", "choices": [{"media": {"image": "happy.jpg"}, "name": "happy"}, {"media": {"image": "sad.jpg"}, "name": "sad"}]}, {"control": {"appearance": "list-nolabel"}, "name": "happy_sad_brian", "hint": "This is a user-defined hint for the 2nd row", "choices": [{"media": {"image": "happy.jpg"}, "name": "happy"}, {"media": {"image": "sad.jpg"}, "name": "sad"}], "label": "Brian", "type": "select all that apply"}, {"control": {"appearance": "list-nolabel"}, "name": "happy_sad_michael", "hint": "This is a user-defined hint for the 3rd row", "choices": [{"media": {"image": "happy.jpg"}, "name": "happy"}, {"media": {"image": "sad.jpg"}, "name": "sad"}], "label": "Michael", "type": "select all that apply"}]}, {"control": {"bodyless": true}, "type": "group", "name": "meta", "children": [{"bind": {"readonly": "true()", "calculate": "concat('uuid:', uuid())"}, "type": "calculate", "name": "instanceID"}]}]}
'''

jsontxt = '''{
    "name": "simple_loop", 
    "title": "simple_loop", 
    "sms_keyword": "simple_loop", 
    "default_language": "default", 
    "id_string": "simple_loop", 
    "type": "survey", 
    "children": [
        {
            "children": [
                {
                    "type": "integer", 
                    "name": "count", 
                    "label": {
                        "English": "How many are there in this group?"
                    }
                }
            ], 
            "type": "loop", 
            "name": "my_table", 
            "columns": [
                {
                    "name": "col1", 
                    "label": {
                        "English": "Column 1"
                    }
                }, 
                {
                    "name": "col2", 
                    "label": {
                        "English": "Column 2"
                    }
                }
            ], 
            "label": {
                "English": "My Table"
            }
        }, 
        {
            "control": {
                "bodyless": true
            }, 
            "type": "group", 
            "name": "meta", 
            "children": [
                {
                    "bind": {
                        "readonly": "true()", 
                        "calculate": "concat('uuid:', uuid())"
                    }, 
                    "type": "calculate", 
                    "name": "instanceID"
                }
            ]
        }
    ]
}
'''

def dict_test():
  return json.loads(jsontxt2)

def json_test():
  return jsontxt2
