""" Test TLM Json Parser Functionality """
import pytest
from mock import MagicMock
import data_handling.parsers.tlm_json_parser as tlm_parser

# parseTlmConfJson tests
def test_tlm_json_parser_parseTlmConfJson_returns_configs_with_empty_dicts_when_reorg_dict_is_empty(mocker):
    # Arrange
    arg_file_path = MagicMock()

    fake_data = MagicMock()
    fake_organized_data = {}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = []
    expected_result['test_assignments'] = []
    expected_result['description_assignments'] = []

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

def test_tlm_json_parser_parseTlmConfJson_returns_expected_configs_dict_when_reorg_dict_contains_only_one_label_and_order_key_does_not_exist(mocker):
    # Arrange
    arg_file_path = MagicMock()

    fake_data = MagicMock()
    fake_label = MagicMock()
    fake_subsystem = MagicMock()
    fake_limits = MagicMock()
    fake_mnemonics = MagicMock()
    fake_description = MagicMock()
    fake_organized_data = {}
    fake_organized_data[fake_label] = {'subsystem' : fake_subsystem,
                                       'tests' : {fake_mnemonics : fake_limits},
                                       'description' : fake_description}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = [fake_subsystem]
    expected_result['test_assignments'] = [[[fake_mnemonics, fake_limits]]]
    expected_result['description_assignments'] = [fake_description]

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

def test_tlm_json_parser_parseTlmConfJson_returns_expected_configs_dict_when_reorg_dict_contains_only_one_label_and_limits_test_and_description_keys_do_not_exist(mocker):
    # Arrange
    arg_file_path = MagicMock()

    fake_data = MagicMock()
    fake_label = MagicMock()
    fake_subsystem = MagicMock()
    fake_organized_data = {}
    fake_organized_data[fake_label] = {'subsystem' : fake_subsystem}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = [fake_subsystem]
    expected_result['test_assignments'] = [[['NOOP']]]
    expected_result['description_assignments'] = [['No description']]

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

def test_tlm_json_parser_parseTlmConfJson_returns_expected_configs_dict_when_reorg_dict_contains_multiple_labels_and_limits_test_and_description_keys_do_not_exist(mocker):
    # Arrange
    arg_file_path = MagicMock()

    fake_data = MagicMock()
    fake_organized_data = {}
    fake_subsystems = []
    num_labels = pytest.gen.randint(2, 10) # arbitrary, from 2 to 10
    for i in range(num_labels):
        fake_label = MagicMock()
        fake_subsystem = MagicMock()
        fake_subsystems.append(fake_subsystem)
        fake_organized_data[fake_label] = {'subsystem' : fake_subsystem}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = fake_subsystems
    expected_result['test_assignments'] = [[['NOOP']]] * num_labels
    expected_result['description_assignments'] = [['No description']] * num_labels

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

def test_tlm_json_parser_parseTlmConfJson_returns_expected_configs_dict_when_reorg_dict_contains_only_one_label_and_order_key_does_exist(mocker):
    # Arrange
    arg_file_path = MagicMock()

    fake_label = MagicMock()
    fake_data = {'order' : [fake_label]}
    fake_subsystem = MagicMock()
    fake_limits = MagicMock()
    fake_mnemonics = MagicMock()
    fake_description = MagicMock()
    fake_organized_data = {}
    fake_organized_data[fake_label] = {'subsystem' : fake_subsystem,
                                       'tests' : {fake_mnemonics : fake_limits},
                                       'description' : fake_description}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = [fake_subsystem]
    expected_result['test_assignments'] = [[[fake_mnemonics, fake_limits]]]
    expected_result['description_assignments'] = [fake_description]

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

def test_tlm_json_parser_parseTlmConfJson_returns_expected_configs_dict_when_reorg_dict_contains_more_than_one_label_and_order_key_does_not_exist(mocker):
    # Arrange
    arg_file_path = MagicMock()

    fake_data = MagicMock()
    num_elems = pytest.gen.randint(2, 10) # arbitrary, from 2 to 10
    fake_label = [MagicMock() for i in range(num_elems)]
    fake_subsystem = MagicMock()
    fake_limits = MagicMock()
    fake_mnemonics = MagicMock()
    fake_description = MagicMock()
    fake_organized_data = {}
    for label in fake_label:
        fake_organized_data[label] = {'subsystem' : fake_subsystem,
                                      'tests' : {fake_mnemonics : fake_limits},
                                      'description' : fake_description}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = [fake_subsystem] * num_elems
    expected_result['test_assignments'] = [[[fake_mnemonics, fake_limits]]] * num_elems
    expected_result['description_assignments'] = [fake_description] * num_elems

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

def test_tlm_json_parser_parseTlmConfJson_returns_expected_configs_dict_when_reorg_dict_contains_more_than_one_label_and_order_key_does_exist(mocker):
    # Arrange
    arg_file_path = MagicMock()

    num_elems = pytest.gen.randint(2, 10) # arbitrary, from 2 to 10
    fake_label = []
    fake_subsystem = []
    fake_limits = []
    fake_mnemonics = []
    fake_description = []
    for i in range(num_elems):
        fake_label.append(MagicMock())
        fake_subsystem.append(MagicMock())
        fake_limits.append(MagicMock())
        fake_mnemonics.append(MagicMock())
        fake_description.append(MagicMock())
    fake_order = fake_label.copy()
    pytest.gen.shuffle(fake_order)
    fake_data = {'order' : fake_order}

    desired_order = {}
    for i in range(num_elems):
        desired_order[fake_order[i]] = i

    ordering_list = []
    for label in fake_label:
        ordering_list.append(desired_order[label])
    
    ordered_subsys = [y for x, y in sorted(zip(ordering_list, fake_subsystem))]
    ordered_mnemonics = [y for x, y in sorted(zip(ordering_list, fake_mnemonics))]
    ordered_limits = [y for x, y in sorted(zip(ordering_list, fake_limits))]
    ordered_descs = [y for x, y in sorted(zip(ordering_list, fake_description))]
    
    fake_organized_data = {}
    for i in range(num_elems):
        fake_organized_data[fake_label[i]] = {'subsystem' : fake_subsystem[i],
                                              'tests' : {fake_mnemonics[i] : fake_limits[i]},
                                              'description' : fake_description[i]}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = []
    expected_result['test_assignments'] = []
    expected_result['description_assignments'] = []
    for i in range(num_elems):
        expected_result['subsystem_assignments'].append(ordered_subsys[i])
        expected_result['test_assignments'].append([[ordered_mnemonics[i], ordered_limits[i]]])
        expected_result['description_assignments'].append(ordered_descs[i])

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

def test_tlm_json_parser_parseTlmConfJson_returns_expected_configs_dict_when_reorg_dict_contains_more_than_one_label_and_limits_are_interpreted_as_empty_lists(mocker):
    # Arrange
    arg_file_path = MagicMock()

    num_elems = pytest.gen.randint(2, 10) # arbitrary, from 2 to 10
    fake_label = []
    fake_subsystem = []
    fake_limits = []
    fake_mnemonics = []
    fake_description = []
    for i in range(num_elems):
        fake_label.append(MagicMock())
        fake_subsystem.append(MagicMock())
        fake_limits.append(MagicMock())
        fake_mnemonics.append(MagicMock())
        fake_description.append(MagicMock())
    fake_order = fake_label.copy()
    pytest.gen.shuffle(fake_order)
    fake_data = {'order' : fake_order}

    desired_order = {}
    for i in range(num_elems):
        desired_order[fake_order[i]] = i

    ordering_list = []
    for label in fake_label:
        ordering_list.append(desired_order[label])
    
    ordered_subsys = [y for x, y in sorted(zip(ordering_list, fake_subsystem))]
    ordered_mnemonics = [y for x, y in sorted(zip(ordering_list, fake_mnemonics))]
    ordered_limits = [y for x, y in sorted(zip(ordering_list, fake_limits))]
    ordered_descs = [y for x, y in sorted(zip(ordering_list, fake_description))]
    
    fake_organized_data = {}
    for i in range(num_elems):
        fake_organized_data[fake_label[i]] = {'subsystem' : fake_subsystem[i],
                                              'tests' : {fake_mnemonics[i] : fake_limits[i]},
                                              'description' : fake_description[i]}

    mocker.patch('data_handling.parsers.tlm_json_parser.parseJson', return_value=fake_data)
    mocker.patch('data_handling.parsers.tlm_json_parser.reorganizeTlmDict', return_value=fake_organized_data)

    expected_result = {}
    expected_result['subsystem_assignments'] = []
    expected_result['test_assignments'] = []
    expected_result['description_assignments'] = []
    for i in range(num_elems):
        expected_result['subsystem_assignments'].append(ordered_subsys[i])
        expected_result['test_assignments'].append([[ordered_mnemonics[i], ordered_limits[i]]])
        expected_result['description_assignments'].append(ordered_descs[i])

    # Act
    result = tlm_parser.parseTlmConfJson(arg_file_path)

    # Assert
    assert tlm_parser.parseJson.call_count == 1
    assert tlm_parser.parseJson.call_args_list[0].args == (arg_file_path, )
    assert tlm_parser.reorganizeTlmDict.call_count == 1
    assert tlm_parser.reorganizeTlmDict.call_args_list[0].args == (fake_data, )
    assert result == expected_result

# reorganizeTlmDict tests
def test_tlm_json_parser_reorganizeTlmDict_raises_error_when_arg_data_does_not_contain_subsystems_key():
    # Arrange
    arg_data_len = pytest.gen.randint(0, 10) # arbitrary, from 0 to 10
    arg_data = {}
    [arg_data.update({MagicMock() : MagicMock()}) for i in range(arg_data_len)]

    # Assert
    with pytest.raises(KeyError) as e_info:
        result = tlm_parser.reorganizeTlmDict(arg_data)

    # Act
    assert e_info.match('subsystems')

def test_tlm_json_parser_reorganizeTlmDict_returns_empty_dict_when_arg_data_subsystems_exists_and_is_empty():
    # Arrange
    arg_data_len = pytest.gen.randint(0, 10) # arbitrary, from 0 to 10
    arg_data = {}
    [arg_data.update({MagicMock() : MagicMock()}) for i in range(arg_data_len)]
    arg_data.update({'subsystems' : {}})

    # Assert
    result = tlm_parser.reorganizeTlmDict(arg_data)

    # Act
    assert result == {}

def test_tlm_json_parser_reorganizeTlmDict_returns_expected_dict_when_arg_data_subsystems_exists_and_is_not_empty(mocker):
    # Arrange
    num_subsystems = pytest.gen.randint(1, 10) # arbitrary, from 1 to 10
    fake_subsystems = [MagicMock() for i in range(num_subsystems)]

    arg_data_len = pytest.gen.randint(0, 10) # arbitrary, from 0 to 10
    arg_data = {}
    [arg_data.update({MagicMock() : MagicMock()}) for i in range(arg_data_len)]
    arg_data.update({'subsystems' : {}})
    expected_result = {}
    for ss in fake_subsystems:
        arg_data['subsystems'].update({ss : {}})
        num_fake_apps = pytest.gen.randint(0, 10) # arbitrary, from 0 to 10
        for i in range(num_fake_apps):
            fake_label = MagicMock()
            fake_data = {MagicMock() : MagicMock()}
            arg_data['subsystems'][ss].update({fake_label : fake_data})
            expected_result.update({fake_label : fake_data})
            expected_result[fake_label]['subsystem'] = ss

    # Assert
    result = tlm_parser.reorganizeTlmDict(arg_data)

    # Act
    assert result == expected_result

# str2lst tests
def test_tlm_json_parser_str2lst_returns_call_to_ast_literal_eval_which_receive_given_string(mocker):
    # Arrange
    arg_string = str(MagicMock())

    expected_result = MagicMock()
    
    mocker.patch('data_handling.parsers.tlm_json_parser.ast.literal_eval', return_value=expected_result)

    # Act
    result = tlm_parser.str2lst(arg_string)

    # Assert
    assert tlm_parser.ast.literal_eval.call_count == 1
    assert tlm_parser.ast.literal_eval.call_args_list[0].args == (arg_string, )
    assert result == expected_result

def test_tlm_json_parser_str2lst_prints_message_when_ast_literal_eval_receives_given_string_but_raises_exception(mocker):
    # Arrange
    arg_string = str(MagicMock())
    
    mocker.patch('data_handling.parsers.tlm_json_parser.ast.literal_eval', side_effect=Exception)
    mocker.patch('data_handling.parsers.tlm_json_parser.print')
    
    # Act
    result = tlm_parser.str2lst(arg_string)

    # Assert
    assert tlm_parser.ast.literal_eval.call_count == 1
    assert tlm_parser.ast.literal_eval.call_args_list[0].args == (arg_string, )
    assert tlm_parser.print.call_count == 1
    assert tlm_parser.print.call_args_list[0].args == ("Unable to process string representation of list", )
    assert result == None

# parseJson tests
def test_tlm_json_parser_parseJson_opens_given_path_and_returns_data_returned_by_orjson(mocker):
    # Arrange
    arg_path = MagicMock()

    fake_file = MagicMock()
    fake_file_str = MagicMock()
    fake_file_data = MagicMock()

    mocker.patch('data_handling.parsers.tlm_json_parser.open', return_value=fake_file)
    mocker.patch.object(fake_file, 'read', return_value=fake_file_str)
    mocker.patch('data_handling.parsers.tlm_json_parser.orjson.loads', return_value=fake_file_data)
    mocker.patch.object(fake_file, 'close')

    # Act
    result = tlm_parser.parseJson(arg_path)
    
    # Assert
    assert tlm_parser.open.call_count == 1
    assert tlm_parser.open.call_args_list[0].args == (arg_path, 'rb')
    assert fake_file.read.call_count == 1
    assert tlm_parser.orjson.loads.call_count == 1
    assert tlm_parser.orjson.loads.call_args_list[0].args == (fake_file_str, )
    assert fake_file.close.call_count == 1
    assert result == fake_file_data