# GSC-19165-1, "The On-Board Artificial Intelligence Research (OnAIR) Platform"
#
# Copyright © 2023 United States Government as represented by the Administrator of
# the National Aeronautics and Space Administration. No copyright is claimed in the
# United States under Title 17, U.S. Code. All Other Rights Reserved.
#
# Licensed under the NASA Open Source Agreement version 1.3
# See "NOSA GSC-19165-1 OnAIR.pdf"

<<<<<<< HEAD
import pytest
from unittest.mock import MagicMock, PropertyMock

import onair.data_handling.sbn_adapter as sbn_adapter
from onair.data_handling.sbn_adapter import AdapterDataSource

from importlib import reload
import sys

@pytest.fixture
def setup_teardown():
    # # refresh sbn_adapter module before each test to ensure independence 
    reload(sbn_adapter)
    
    print('setup')
    
    pytest.cut = AdapterDataSource.__new__(AdapterDataSource)
    yield 'setup_teardown'

    print('teardown')

    # refresh message_headers module after each test to remove any changes from testing
    del sys.modules['message_headers']
    mh = MagicMock()
    mh.sample_data_tlm_t = MagicMock()
    mh.sample_data_tlm_t.__name__ = 'mock_sample_data_tlm_t'
    mh.sample_data_power_t = MagicMock()
    mh.sample_data_power_t.__name__ = 'mock_sample_data_power_t'
    mh.sample_data_thermal_t = MagicMock()
    mh.sample_data_thermal_t.__name__ = 'mock_sample_data_thermal_t'
    mh.sample_data_gps_t = MagicMock()
    mh.sample_data_gps_t.__name__ = 'mock_sample_data_gps_t'
    sys.modules['message_headers'] = mh


class FakeSbnDataGenericT(MagicMock):
    pass

class FakeDataStruct(MagicMock):
    pass

# testing that the msgID_lookup_table is as we expect allows us to safely reference it in other tests
def test_sbn_adapter_msgID_lookup_table_is_expected_value():
    # Arrange
    expected_msgID_lookup_table = {0x0885 : ["SAMPLE", sbn_adapter.msg_hdr.sample_data_tlm_t],
                                   0x0887 : ["SAMPLE", sbn_adapter.msg_hdr.sample_data_power_t],
                                   0x0889 : ["SAMPLE", sbn_adapter.msg_hdr.sample_data_thermal_t],
                                   0x088A : ["SAMPLE", sbn_adapter.msg_hdr.sample_data_gps_t]}

    # Act
    # Assert
    assert sbn_adapter.msgID_lookup_table == expected_msgID_lookup_table

def test_sbn_adapter_message_listener_thread_loops_indefinitely_until_purposely_broken(mocker, setup_teardown):
    # Arrange
    fake_generic_recv_msg_p = MagicMock()
    fake_recv_msg_p = MagicMock()

    fake_sbn = MagicMock()
    fake_sbn.sbn_data_generic_t = PropertyMock()

    fake_generic_recv_msg_p_contents = PropertyMock()
    fake_generic_recv_msg_p_TlmHeader = PropertyMock()
    fake_generic_recv_msg_p_Primary = PropertyMock()
    
    fake_generic_recv_msg_p.contents = fake_generic_recv_msg_p_contents
    fake_generic_recv_msg_p.contents.TlmHeader = fake_generic_recv_msg_p_TlmHeader
    fake_generic_recv_msg_p.contents.TlmHeader.Primary = fake_generic_recv_msg_p_Primary
    fake_msgID = pytest.gen.choice(list(sbn_adapter.msgID_lookup_table.keys()))
    fake_generic_recv_msg_p.contents.TlmHeader.Primary.StreamId = fake_msgID

    # this exception will be used to forcefully exit the message_listener_thread function's while(True) loop
    exception_message = 'forced loop exit'
    exit_exception = Exception(exception_message)
    
    # sets return value of POINTER function to return fake_pointer an arbitrary number of times, then return exit_exception
    num_loop_iterations = pytest.gen.randint(1, 10) # arbitrary, 1 to 10
    side_effect_list = ([''] * num_loop_iterations) # one item for each loop
    side_effect_list.append(exit_exception) # short-circuit exit while(True) loop

    fake__fields_ = [["1st item placeholder"]]
    num_fake_prints = pytest.gen.randint(1, 10) # arbitrary from 1 to 10
    fake_field_names = []
    fake_attr_values = []
    expected_print_string = ''
    for i in range(num_fake_prints):
        fake_attr_name = str(MagicMock())

        print(f"fake_attr_name ", i, " ", fake_attr_name)
        fake_attr_value = MagicMock()

        print(f"fake_attr_value ", i, " ", fake_attr_value)
        fake_field_names.append(fake_attr_name)
        fake_attr_values.append(fake_attr_value)
        fake__fields_.append([fake_attr_name, fake_attr_value])
        expected_print_string  += fake_attr_name + ": " + str(fake_attr_value) + ", " 

    fake_generic_recv_msg_p_contents._fields_ = fake__fields_
    expected_print_string = expected_print_string[0:-2]

    mocker.patch(sbn_adapter.__name__ + '.sbn', fake_sbn)
    pointer_side_effects = [FakeSbnDataGenericT, FakeDataStruct] * (num_loop_iterations + 1)
    mocker.patch(sbn_adapter.__name__ + '.POINTER', side_effect=pointer_side_effects)
    mocker.patch.object(FakeSbnDataGenericT, '__new__', return_value=fake_generic_recv_msg_p)
    mocker.patch.object(fake_sbn, 'recv_msg', return_value=None)
    mocker.patch.object(FakeDataStruct, '__new__', return_value=fake_recv_msg_p)
    mocker.patch(sbn_adapter.__name__ + '.getattr', side_effect=fake_attr_values * (num_loop_iterations + 1))
    mocker.patch(sbn_adapter.__name__ + '.print', return_value=None)

    mocker.patch(sbn_adapter.__name__ + '.get_current_data', side_effect=side_effect_list)
    
    # Act
    with pytest.raises(Exception) as e_info:
        sbn_adapter.message_listener_thread()

    # Assert
    assert e_info.match(exception_message)
    assert sbn_adapter.POINTER.call_count == (num_loop_iterations + 1) * 2
    for i in range(num_loop_iterations + 1):
        assert sbn_adapter.POINTER.call_args_list[i*2].args == (fake_sbn.sbn_data_generic_t, )
        assert sbn_adapter.POINTER.call_args_list[(i*2)+1].args == (sbn_adapter.msgID_lookup_table[fake_msgID][1], )
    assert FakeSbnDataGenericT.__new__.call_count == num_loop_iterations + 1
    assert FakeDataStruct.__new__.call_count == num_loop_iterations + 1
    assert fake_sbn.recv_msg.call_count == num_loop_iterations + 1
    for i in range(num_loop_iterations + 1):
        assert fake_sbn.recv_msg.call_args_list[i].args == (fake_generic_recv_msg_p, )
    assert sbn_adapter.getattr.call_count == (num_loop_iterations + 1) * num_fake_prints
    for i in range((num_loop_iterations + 1) * num_fake_prints):
        assert sbn_adapter.getattr.call_args_list[i].args == (fake_generic_recv_msg_p_contents, fake_field_names[i % len(fake_field_names)])
    assert sbn_adapter.print.call_count == num_loop_iterations + 1
    for i in range(num_loop_iterations + 1):
        assert sbn_adapter.print.call_args_list[i].args == (expected_print_string, )
    assert sbn_adapter.get_current_data.call_count == num_loop_iterations + 1
    for i in range(num_loop_iterations + 1):
        assert sbn_adapter.get_current_data.call_args_list[i].args == (fake_generic_recv_msg_p_contents, sbn_adapter.msgID_lookup_table[fake_msgID][1], sbn_adapter.msgID_lookup_table[fake_msgID][0])
  
def test_get_current_data_with_no_fields_in_recv_msg_or_data_struct(mocker, setup_teardown):
    # Arrange
    fake_generic_recv_msg_p = MagicMock()

    fake_AdapterDataSource = MagicMock
    fake_AdapterDataSource.currentData = {}
    fake_AdapterDataSource.double_buffer_read_index = 1
    fake_AdapterDataSource.new_data_lock = PropertyMock()
    fake_current_buffer = {}
    fake_current_buffer['data'] = ['placeholder']

    fake_AdapterDataSource.currentData[0] = fake_current_buffer

    arg_recv_msg = PropertyMock()
    fake_generic_recv_msg_p_TlmHeader = PropertyMock()
    fake_generic_recv_msg_p_Primary = PropertyMock()
    fake_recv_msg_p_Secondary = PropertyMock()
    
    fake_generic_recv_msg_p.contents = arg_recv_msg
    fake_generic_recv_msg_p.contents.TlmHeader = fake_generic_recv_msg_p_TlmHeader
    fake_generic_recv_msg_p.contents.TlmHeader.Primary = fake_generic_recv_msg_p_Primary
    fake_msgID = pytest.gen.choice(list(sbn_adapter.msgID_lookup_table.keys()))
    fake_generic_recv_msg_p.contents.TlmHeader.Primary.StreamId = fake_msgID
    arg_recv_msg.TlmHeader.Secondary = fake_recv_msg_p_Secondary
    fake_seconds = pytest.gen.randint(0,59)
    fake_recv_msg_p_Secondary.Seconds = fake_seconds
    fake_subseconds = pytest.gen.randint(0,999)
    fake_recv_msg_p_Secondary.Subseconds = fake_subseconds
    fake_start_time = MagicMock()
    fake_timedelta = MagicMock()
    fake_time = MagicMock()
    fake_str_time = MagicMock()

    mocker.patch(sbn_adapter.__name__ + '.AdapterDataSource',fake_AdapterDataSource)
    mocker.patch(sbn_adapter.__name__ + '.datetime.datetime', return_value=fake_start_time)
    mocker.patch(sbn_adapter.__name__ + '.datetime.timedelta', return_value=fake_timedelta)
    mocker.patch.object(fake_start_time, '__add__', return_value=fake_time)
    mocker.patch.object(fake_time, 'strftime', return_value=fake_str_time)
    fake_AdapterDataSource.new_data = False # not required, but helps verify it gets changed to True
    mocker.patch.object(fake_AdapterDataSource.new_data_lock, '__enter__') # __enter__ is used by keyword 'with' in python

    arg_data_struct = sbn_adapter.msgID_lookup_table[fake_msgID][1]
    arg_app_name = sbn_adapter.msgID_lookup_table[fake_msgID][0]

    # Act
    sbn_adapter.get_current_data(arg_recv_msg, arg_data_struct, arg_app_name)

    # Assert
    assert sbn_adapter.datetime.datetime.call_count ==  1
    assert sbn_adapter.datetime.datetime.call_args_list[0].args == (1969, 12, 31, 20)
    assert sbn_adapter.datetime.timedelta.call_count == 1
    assert sbn_adapter.datetime.timedelta.call_args_list[0].kwargs == {'seconds':fake_seconds  + (2**(-32) * fake_subseconds)}
    # Although patched and does return value, fake_start_time.__add__ does not count but leaving comments here to show we would do this if able
    # assert fake_start_time.__add__.call_count == num_loop_iterations + 1
    # for i in range(num_loop_iterations + 1):
    #     assert fake_start_time.__add__.call_args_list[i].args == (fake_timedelta, )
    assert fake_time.strftime.call_count == 1
    assert fake_time.strftime.call_args_list[0].args == ("%Y-%j-%H:%M:%S.%f", )
    assert fake_AdapterDataSource.new_data == True
    assert fake_current_buffer['data'][0] == fake_str_time
    
def test_get_current_data_with_fields_in_recv_msg_and_data_struct(mocker, setup_teardown):
    # Arrange
    fake_generic_recv_msg_p = MagicMock()

    fake_AdapterDataSource = MagicMock()
    fake_AdapterDataSource.currentData = {}
    fake_AdapterDataSource.double_buffer_read_index = 1
    fake_AdapterDataSource.new_data_lock = PropertyMock()
    fake_AdapterDataSource.new_data_lock.__enter__ = MagicMock()
    fake_AdapterDataSource.new_data_lock.__exit__ = MagicMock()
    fake_current_buffer = {}
    fake_current_buffer['data'] = ['placeholder0', 'placeholder1']
    fake_headers_for_current_buffer = MagicMock()
    fake_current_buffer['headers'] = fake_headers_for_current_buffer
    fake_idx = 1
    fake_AdapterDataSource.currentData[0] = fake_current_buffer
    arg_recv_msg = PropertyMock()
    fake_generic_recv_msg_p_TlmHeader = PropertyMock()
    fake_generic_recv_msg_p_Primary = PropertyMock()
    fake_recv_msg_p_Secondary = PropertyMock()
    
    fake_generic_recv_msg_p.contents = arg_recv_msg
    fake_generic_recv_msg_p.contents.TlmHeader = fake_generic_recv_msg_p_TlmHeader
    fake_generic_recv_msg_p.contents.TlmHeader.Primary = fake_generic_recv_msg_p_Primary
    fake_msgID = pytest.gen.choice(list(sbn_adapter.msgID_lookup_table.keys()))
    fake_generic_recv_msg_p.contents.TlmHeader.Primary.StreamId = fake_msgID
    arg_recv_msg.TlmHeader.Secondary = fake_recv_msg_p_Secondary
    fake_seconds = pytest.gen.randint(0,59)
    fake_recv_msg_p_Secondary.Seconds = fake_seconds
    fake_subseconds = pytest.gen.randint(0,999)
    fake_recv_msg_p_Secondary.Subseconds = fake_subseconds
    fake_start_time = MagicMock()
    fake_timedelta = MagicMock()
    fake_time = MagicMock()
    fake_str_time = MagicMock()

    fake__fields_ = [["1st item placeholder"]]
    num_fake__fields_ = pytest.gen.randint(1, 10) # arbitrary from 1 to 10
    fake_field_names = []
    for i in range(num_fake__fields_):
        fake_attr_name = str(MagicMock())
        fake_attr_value = MagicMock()
        
        fake_field_names.append(fake_attr_name)
        arg_recv_msg.__setattr__(fake_attr_name, fake_attr_value)
        sbn_adapter.msgID_lookup_table[fake_msgID][1].__setattr__(fake_attr_name, fake_attr_value)
        fake__fields_.append([fake_attr_name, fake_attr_value])

    arg_recv_msg._fields_ = fake__fields_
    sbn_adapter.msgID_lookup_table[fake_msgID][1]._fields_ = fake__fields_

    mocker.patch(sbn_adapter.__name__ + '.AdapterDataSource',fake_AdapterDataSource)
    mocker.patch(sbn_adapter.__name__ + '.datetime.datetime', return_value=fake_start_time)
    mocker.patch(sbn_adapter.__name__ + '.datetime.timedelta', return_value=fake_timedelta)
    mocker.patch.object(fake_start_time, '__add__', return_value=fake_time)
    mocker.patch.object(fake_time, 'strftime', return_value=fake_str_time)
    fake_AdapterDataSource.new_data = False # not required, but helps verify it gets changed to True
    mocker.patch.object(fake_AdapterDataSource.new_data_lock, '__enter__') # __enter__ is used by keyword 'with' in python
    mocker.patch.object(fake_headers_for_current_buffer, 'index', return_value=fake_idx)

    arg_data_struct = sbn_adapter.msgID_lookup_table[fake_msgID][1]
    arg_app_name = sbn_adapter.msgID_lookup_table[fake_msgID][0]

    # Act
    sbn_adapter.get_current_data(arg_recv_msg, arg_data_struct, arg_app_name)

    # Assert
    assert sbn_adapter.datetime.datetime.call_count == 1
    assert sbn_adapter.datetime.datetime.call_args_list[0].args == (1969, 12, 31, 20)
    assert sbn_adapter.datetime.timedelta.call_count == 1
    assert sbn_adapter.datetime.timedelta.call_args_list[0].kwargs == {'seconds':fake_seconds  + (2**(-32) * fake_subseconds)}
    # Although patched and does return value, fake_start_time.__add__ does not count but leaving comments here to show we would do this if able
    # assert fake_start_time.__add__.call_count == num_loop_iterations + 1
    # for i in range(num_loop_iterations + 1):
    #     assert fake_start_time.__add__.call_args_list[i].args == (fake_timedelta, )
    assert fake_time.strftime.call_count == 1
    assert fake_time.strftime.call_args_list[0].args == ("%Y-%j-%H:%M:%S.%f", )
    assert fake_headers_for_current_buffer.index.call_count == num_fake__fields_
    for i in range(num_fake__fields_):
        assert fake_headers_for_current_buffer.index.call_args_list[i].args == (str((sbn_adapter.msgID_lookup_table[fake_msgID][0]) + "." + str(sbn_adapter.msgID_lookup_table[fake_msgID][1].__name__) + "." + fake_field_names[i]), )
    assert fake_AdapterDataSource.new_data == True
    assert fake_current_buffer['data'][0] == fake_str_time

# ---------- Tests for AdapterDataSource class ---------

# tests for AdapterDataSource variables
def test_sbn_adapter_AdapterDataSource_current_data_equals_expected_value_when_no__fields__exist_in_data_struct(setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    lookup_table = sbn_adapter.msgID_lookup_table

    expected_current_data = []

    for x in range(2):
        expected_current_data.append({'headers' : [], 'data' : []})
        expected_current_data[x]['headers'].append('TIME')
        expected_current_data[x]['data'].append('2000-001-12:00:00.000000000')

        for msgID in lookup_table.keys():
            app_name, data_struct = lookup_table[msgID]
            struct_name = data_struct.__name__
            expected_current_data[x]['data'].extend([0]*len(data_struct._fields_[1:])) #initialize all the data arrays with zero

    # Act
    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Assert
    assert cut.currentData == expected_current_data

def test_sbn_adapter_AdapterDataSource_current_data_equals_expected_value_when__fields___do_exist_in_data_struct(setup_teardown):
    # Arrange
    lookup_table = sbn_adapter.msgID_lookup_table

    expected_current_data = []

    for x in range(2):
        expected_current_data.append({'headers' : [], 'data' : []})
        expected_current_data[x]['headers'].append('TIME')
        expected_current_data[x]['data'].append('2000-001-12:00:00.000000000')
        for msgID in lookup_table.keys():
            app_name, data_struct = lookup_table[msgID]
            struct_name = data_struct.__name__

            fake__fields_ = [["1st item placeholder"]]
            num_fake__fields_ = 1#pytest.gen.randint(1, 10) # arbitrary from 1 to 10
            fake_field_names = []
            
            for i in range(num_fake__fields_):
                fake_attr_name = "fake_attr_name"
                fake_attr_value = MagicMock()
                fake_field_names.append(fake_attr_name)
                fake__fields_.append([fake_attr_name, fake_attr_value])

            data_struct._fields_ = fake__fields_
            sbn_adapter.msgID_lookup_table[msgID][1].__setattr__('_fields_', fake__fields_)
                
            for field_name, field_type in data_struct._fields_[1:]:
                expected_current_data[x]['headers'].append('{}.{}.{}'.format(app_name, struct_name, str(field_name)))
    
            expected_current_data[x]['data'].extend([0]*num_fake__fields_) #initialize all the data arrays with zero
    
    # Renew abn_adapter and AdapterDataSource to ensure test independence and get field updates to message_headers module
    reload(sbn_adapter)
    AdapterDataSource = sbn_adapter.AdapterDataSource
    
    # Act
    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Assert
    assert cut.currentData == expected_current_data

# tests for AdapterDataSource.connect
def test_sbn_adapter_AdapterDataSource_connect_when_msgID_lookup_table_has_zero_keys(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    fake_listener_thread = MagicMock()
    fake_msgID_lookup_table = MagicMock()
    fake_msgID_lookup_table_keys = []

    mocker.patch(sbn_adapter.__name__ + '.time.sleep')
    mocker.patch(sbn_adapter.__name__ + '.os.chdir')
    mocker.patch(sbn_adapter.__name__ + '.sbn.sbn_load_and_init')
    mocker.patch(sbn_adapter.__name__ + '.message_listener_thread', fake_listener_thread)
    mocker.patch(sbn_adapter.__name__ + '.threading.Thread', return_value=fake_listener_thread)
    mocker.patch.object(fake_listener_thread, 'start')
    mocker.patch(sbn_adapter.__name__ + '.msgID_lookup_table', fake_msgID_lookup_table)
    mocker.patch.object(fake_msgID_lookup_table, 'keys', return_value=fake_msgID_lookup_table_keys)
    mocker.patch(sbn_adapter.__name__ + '.sbn.subscribe')
    
    cut = AdapterDataSource.__new__(AdapterDataSource)

=======
# testing packages
import pytest
from unittest.mock import MagicMock, PropertyMock

# mock dependencies of sbn_adapter.py
import sys
sys.modules['sbn_python_client'] = MagicMock()
sys.modules['message_headers'] = MagicMock()

import onair.data_handling.sbn_adapter as sbn_adapter
from onair.data_handling.sbn_adapter import DataSource
from onair.data_handling.on_air_data_source import OnAirDataSource
from onair.data_handling.on_air_data_source import ConfigKeyError

import threading
import datetime
import copy
import json

# __init__ tests
def test_sbn_adapter_DataSource__init__sets_values_then_connects(mocker):
    # Arrange
    arg_data_file = MagicMock()
    arg_meta_file = MagicMock()
    arg_ss_breakdown = MagicMock()

    fake_new_data_lock = MagicMock()

    cut = DataSource.__new__(DataSource)

    mocker.patch.object(OnAirDataSource, '__init__', new=MagicMock())
    mocker.patch('threading.Lock', return_value=fake_new_data_lock)
    mocker.patch.object(cut, 'connect')

    # Act
    cut.__init__(arg_data_file, arg_meta_file, arg_ss_breakdown)

    # Assert
    assert OnAirDataSource.__init__.call_count == 1
    assert OnAirDataSource.__init__.call_args_list[0].args == (arg_data_file, arg_meta_file, arg_ss_breakdown)
    assert cut.new_data_lock == fake_new_data_lock
    assert cut.new_data == False
    assert cut.double_buffer_read_index == 0
    assert cut.connect.call_count == 1
    assert cut.connect.call_args_list[0].args == ()

# connect tests
def test_sbn_adapter_DataSource_connect_starts_listener_thread_and_subscribes_to_messages(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)
    mocker.patch(sbn_adapter.__name__+'.time.sleep')
    mocker.patch(sbn_adapter.__name__+'.os.chdir')
    mocker.patch(sbn_adapter.__name__+'.sbn.sbn_load_and_init')
    fake_listener_thread = MagicMock()
    mocker.patch(sbn_adapter.__name__+'.threading.Thread', return_value = fake_listener_thread)
    mocker.patch(sbn_adapter.__name__+'.sbn.subscribe')

    
    fake_msgID_lookup_table = {}
    n_ids = pytest.gen.randint(0,9)
    while len(fake_msgID_lookup_table) < n_ids:
        fake_id = pytest.gen.randint(0,1000)
        fake_msgID_lookup_table[fake_id] = "na"
    
    cut.__setattr__('msgID_lookup_table',fake_msgID_lookup_table)
    
>>>>>>> c1b3f1d03fa45a6b7b8f96c00999452800972810
    # Act
    cut.connect()

    # Assert
    assert sbn_adapter.time.sleep.call_count == 1
<<<<<<< HEAD
    assert sbn_adapter.time.sleep.call_args_list[0].args == (2,)
    assert sbn_adapter.os.chdir.call_count == 1
    assert sbn_adapter.os.chdir.call_args_list[0].args == ('cf',)
    assert sbn_adapter.sbn.sbn_load_and_init.call_count == 1
    
    assert sbn_adapter.threading.Thread.call_count == 1
    assert sbn_adapter.threading.Thread.call_args_list[0].args == ()
    assert sbn_adapter.threading.Thread.call_args_list[0].kwargs == {'target' : fake_listener_thread}
    assert fake_listener_thread.start.call_count == 1

    assert fake_msgID_lookup_table.keys.call_count == 1
    assert sbn_adapter.sbn.subscribe.call_count == 0

def test_sbn_adapter_AdapterDataSource_connect_when_msgID_lookup_table_has_one_key(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    fake_listener_thread = MagicMock()
    fake_msgID_lookup_table = MagicMock()
    fake_msgID = MagicMock()
    fake_msgID_lookup_table_keys = [fake_msgID]

    mocker.patch(sbn_adapter.__name__ + '.time.sleep')
    mocker.patch(sbn_adapter.__name__ + '.os.chdir')
    mocker.patch(sbn_adapter.__name__ + '.sbn.sbn_load_and_init')
    mocker.patch(sbn_adapter.__name__ + '.message_listener_thread', fake_listener_thread)
    mocker.patch(sbn_adapter.__name__ + '.threading.Thread', return_value=fake_listener_thread)
    mocker.patch.object(fake_listener_thread, 'start')
    mocker.patch(sbn_adapter.__name__ + '.msgID_lookup_table', fake_msgID_lookup_table)
    mocker.patch.object(fake_msgID_lookup_table, 'keys', return_value=fake_msgID_lookup_table_keys)
    mocker.patch(sbn_adapter.__name__ + '.sbn.subscribe')
    
    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Act
    cut.connect()

    # Assert
    assert sbn_adapter.time.sleep.call_count == 1
    assert sbn_adapter.time.sleep.call_args_list[0].args == (2,)
    assert sbn_adapter.os.chdir.call_count == 1
    assert sbn_adapter.os.chdir.call_args_list[0].args == ('cf',)
    assert sbn_adapter.sbn.sbn_load_and_init.call_count == 1
    
    assert sbn_adapter.threading.Thread.call_count == 1
    assert sbn_adapter.threading.Thread.call_args_list[0].args == ()
    assert sbn_adapter.threading.Thread.call_args_list[0].kwargs == {'target' : fake_listener_thread}
    assert fake_listener_thread.start.call_count == 1

    assert fake_msgID_lookup_table.keys.call_count == 1
    assert sbn_adapter.sbn.subscribe.call_count == 1
    assert sbn_adapter.sbn.subscribe.call_args_list[0].args == (fake_msgID,)
    
def test_sbn_adapter_AdapterDataSource_connect_when_msgID_lookup_table_has_multiple_keys(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    fake_listener_thread = MagicMock()
    fake_msgID_lookup_table = MagicMock()
    num_keys = pytest.gen.randint(2, 10) # arbitrary, from 2 to 10
    fake_msgID_lookup_table_keys = []
    for i in range(num_keys):
        fake_msgID_lookup_table_keys.append(MagicMock())

    mocker.patch(sbn_adapter.__name__ + '.time.sleep')
    mocker.patch(sbn_adapter.__name__ + '.os.chdir')
    mocker.patch(sbn_adapter.__name__ + '.sbn.sbn_load_and_init')
    mocker.patch(sbn_adapter.__name__ + '.message_listener_thread', fake_listener_thread)
    mocker.patch(sbn_adapter.__name__ + '.threading.Thread', return_value=fake_listener_thread)
    mocker.patch.object(fake_listener_thread, 'start')
    mocker.patch(sbn_adapter.__name__ + '.msgID_lookup_table', fake_msgID_lookup_table)
    mocker.patch.object(fake_msgID_lookup_table, 'keys', return_value=fake_msgID_lookup_table_keys)
    mocker.patch(sbn_adapter.__name__ + '.sbn.subscribe')
    
    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Act
    cut.connect()

    # Assert
    assert sbn_adapter.time.sleep.call_count == 1
    assert sbn_adapter.time.sleep.call_args_list[0].args == (2,)
    assert sbn_adapter.os.chdir.call_count == 1
    assert sbn_adapter.os.chdir.call_args_list[0].args == ('cf',)
    assert sbn_adapter.sbn.sbn_load_and_init.call_count == 1
    
    assert sbn_adapter.threading.Thread.call_count == 1
    assert sbn_adapter.threading.Thread.call_args_list[0].args == ()
    assert sbn_adapter.threading.Thread.call_args_list[0].kwargs == {'target' : fake_listener_thread}
    assert fake_listener_thread.start.call_count == 1

    assert fake_msgID_lookup_table.keys.call_count == 1
    assert sbn_adapter.sbn.subscribe.call_count == num_keys
    for i in range(num_keys):
        assert sbn_adapter.sbn.subscribe.call_args_list[i].args == (fake_msgID_lookup_table_keys[i],)
    
# tests for AdapterDataSource.subscribe_message
def test_sbn_adapter_AdapterDataSource_subscribe_message_when_msgid_is_not_a_list(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    arg_msgid = MagicMock()
    
    mocker.patch(sbn_adapter.__name__ + '.sbn.subscribe')

    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Act
    cut.subscribe_message(arg_msgid)

    # Assert
    assert sbn_adapter.sbn.subscribe.call_count == 1
    assert sbn_adapter.sbn.subscribe.call_args_list[0].args == (arg_msgid,)

def test_sbn_adapter_AdapterDataSource_subscribe_message_when_msgid_is_an_empty_list(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    arg_msgid = []
    
    mocker.patch(sbn_adapter.__name__ + '.sbn.subscribe')

    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Act
    cut.subscribe_message(arg_msgid)

    # Assert
    assert sbn_adapter.sbn.subscribe.call_count == 0

def test_sbn_adapter_AdapterDataSource_subscribe_message_when_msgid_is_a_list_with_only_one_element(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    arg_msgid = [MagicMock()]
    
    mocker.patch(sbn_adapter.__name__ + '.sbn.subscribe')

    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Act
    cut.subscribe_message(arg_msgid)

    # Assert
    assert sbn_adapter.sbn.subscribe.call_count == 1
    assert sbn_adapter.sbn.subscribe.call_args_list[0].args == (arg_msgid[0],)

def test_sbn_adapter_AdapterDataSource_subscribe_message_when_msgid_is_a_list_of_multiple_elements(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    list_length = pytest.gen.randint(2,10) # arbitrary, from 2 to 10
    arg_msgid = []
    for i in range(list_length):
        arg_msgid.append(MagicMock())
    
    mocker.patch(sbn_adapter.__name__ + '.sbn.subscribe')

    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Act
    cut.subscribe_message(arg_msgid)

    # Assert
    assert sbn_adapter.sbn.subscribe.call_count == list_length
    for i in range(list_length):
        assert sbn_adapter.sbn.subscribe.call_args_list[i].args == (arg_msgid[i],)
    
# tests for AdapterDataSource.get_next
def test_sbn_adapter_AdapterDataSource_get_next_when_new_data_is_true(setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    cut = AdapterDataSource.__new__(AdapterDataSource)
    AdapterDataSource.new_data = True
    pre_call_index = AdapterDataSource.double_buffer_read_index
=======
    assert sbn_adapter.os.chdir.call_count == 2
    assert sbn_adapter.os.chdir.call_args_list[0].args == ("cf",)
    assert sbn_adapter.os.chdir.call_args_list[1].args == ("../",)
    assert sbn_adapter.threading.Thread.call_count == 1
    assert fake_listener_thread.start.call_count == 1
    assert sbn_adapter.sbn.subscribe.call_count == n_ids

    subbed_message_ids = set()
    for call in sbn_adapter.sbn.subscribe.call_args_list:
        for arg in call.args:
            subbed_message_ids.add(arg)

    assert subbed_message_ids == set(fake_msgID_lookup_table.keys())

# gather_field_names tests
def test_sbn_adapter_DataSource_gather_field_names_returns_field_name_if_type_not_defined_in_message_headers_and_no_subfields_available(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)

    field_name = MagicMock()
    field_type = MagicMock()

    # field type was not defined in message_headers.py and has no subfields of its own
    field_type.__str__ = MagicMock()
    field_type.__str__.return_value = 'fooble'
    del field_type._fields_

    # Act
    result = cut.gather_field_names(field_name, field_type)

    # Assert
    assert result == [field_name]

def test_sbn_adapter_Data_Source_gather_field_names_returns_nested_list_for_nested_structure(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)

    # parent field has two child fields.
    # The first child field has a grandchild field
    parent_field_name = "parent_field"
    parent_field_type = MagicMock()
    child1_field_name = "child1_field"
    child1_field_type = MagicMock()
    child2_field_name = "child2_field"
    child2_field_type = MagicMock()
    gchild_field_name = "gchild_field"
    gchild_field_type = MagicMock()

    gchild_field_type.__str__ = MagicMock()
    gchild_field_type.__str__.return_value = "message_headers.mock_data_type"
    del gchild_field_type._fields_

    child2_field_type.__str__ = MagicMock()
    child2_field_type.__str__.return_value = "message_headers.mock_data_type"
    del child2_field_type._fields_

    child1_field_type.__str__ = MagicMock()
    child1_field_type.__str__.return_value = "message_headers.mock_data_type"
    child1_field_type._fields_ = [(gchild_field_name, gchild_field_type)]

    parent_field_type.__str__ = MagicMock()
    parent_field_type.__str__.return_value = "message_headers.mock_data_type"
    parent_field_type._fields_ = [(child1_field_name, child1_field_type),
                                               (child2_field_name, child2_field_type)]

    # act
    result = cut.gather_field_names(parent_field_name, parent_field_type)

    # assert
    assert isinstance(result, list)
    assert len(result) == 2
    assert set(result) == set([parent_field_name + '.' + child2_field_name, 
                               parent_field_name + '.' + child1_field_name+ '.' +gchild_field_name])

# parse_meta_data_file tests
def test_sbn_adapter_DataSource_parse_meta_data_file_calls_rasies_ConfigKeyError_when_channels_not_in_config(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)
    arg_meta_data_file = MagicMock()
    arg_ss_breakdown = MagicMock()

    mocker.patch(sbn_adapter.__name__ + '.json.loads', return_value = {})

    # Act
    with pytest.raises(ConfigKeyError) as e_info:
        cut.parse_meta_data_file(arg_meta_data_file,arg_ss_breakdown)

def test_sbn_adapter_DataSource_parse_meta_data_file_populates_lookup_table_and_current_data_on_ideal_config(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)
    arg_meta_data_file = MagicMock()
    arg_ss_breakdown = MagicMock()

    ideal_config = {
        "channels": {
            "0x1": ["AppName1", "DataStruct1"],
            "0x2": ["AppName2", "DataStruct2"]
        }
    }
    
    mock_struct_1 = MagicMock()
    mock_struct_1.__name__ = "DataStruct1"
    mock_struct_1._fields_ = [('TlmHeader', 'type0'), ('field1', 'type1')]

    mock_struct_2 = MagicMock()
    mock_struct_2.__name__ = "DataStruct2"
    mock_struct_2._fields_ = [('field0', 'type0'), ('field1', 'type1')]

    mocker.patch('message_headers.DataStruct1', mock_struct_1)
    mocker.patch('message_headers.DataStruct2', mock_struct_2)

    mocker.patch('builtins.open', mocker.mock_open(read_data=json.dumps(ideal_config)))
    mocker.patch('json.loads', return_value=ideal_config)
    expected_configs = MagicMock()
    mocker.patch(sbn_adapter.__name__ + '.extract_meta_data_handle_ss_breakdown', return_value = expected_configs)

    # Act
    cut.parse_meta_data_file(arg_meta_data_file, arg_ss_breakdown)
    print(cut.currentData)

    # Assert
    assert cut.msgID_lookup_table == {1: ['AppName1', mock_struct_1], 2: ['AppName2', mock_struct_2]}
    assert len(cut.currentData) == 2
    assert len(cut.currentData[0]['headers']) == 2
    assert len(cut.currentData[1]['headers']) == 2
    assert cut.currentData[0]['headers'] == ['AppName1.field1', 'AppName2.field1']
    assert cut.currentData[0]['data'] == [[0], [0]]
    assert cut.currentData[1]['headers'] == ['AppName1.field1', 'AppName2.field1']
    assert cut.currentData[1]['data'] == [[0], [0]]

# process_data_file tests
def test_sbn_adapter_DataSource_process_data_file_does_nothing(mocker):
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_process_data_file_does_nothing
    cut = DataSource.__new__(DataSource)
    arg_data_file = MagicMock()

    expected_result = None

    # Act
    result = cut.process_data_file(arg_data_file)

    # Assert
    assert result == expected_result

# get_vehicle_metadata tests
def test_sbn_adapter_DataSource_get_vehicle_metadata_returns_list_of_headers_and_list_of_test_assignments():
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_get_vehicle_metadata_returns_list_of_headers_and_list_of_test_assignments
    
    # Arrange
    cut = DataSource.__new__(DataSource)
    fake_all_headers = MagicMock()
    fake_test_assignments = MagicMock()
    fake_binning_configs = {}
    fake_binning_configs['test_assignments'] = fake_test_assignments

    expected_result = (fake_all_headers, fake_test_assignments)

    cut.all_headers = fake_all_headers
    cut.binning_configs = fake_binning_configs

    # Act
    result = cut.get_vehicle_metadata()

    # Assert
    assert result == expected_result


# get_next tests
def test_sbn_adapter_DataSource_get_next_returns_expected_data_when_new_data_is_true_and_double_buffer_read_index_is_0():
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_get_next_returns_expected_data_when_new_data_is_true_and_double_buffer_read_index_is_0

    # Arrange
    # Renew DataSource to ensure test independence
    cut = DataSource.__new__(DataSource)
    cut.new_data = True
    cut.new_data_lock = MagicMock()
    cut.double_buffer_read_index = 0
    pre_call_index = cut.double_buffer_read_index
    expected_result = MagicMock()
    cut.currentData = []
    cut.currentData.append({'data': MagicMock()})
    cut.currentData.append({'data': expected_result})
>>>>>>> c1b3f1d03fa45a6b7b8f96c00999452800972810

    # Act
    result = cut.get_next()

    # Assert
<<<<<<< HEAD
    assert AdapterDataSource.new_data == False
    if pre_call_index == 0:
        assert AdapterDataSource.double_buffer_read_index == 1
        assert result == AdapterDataSource.currentData[1]['data']
    elif pre_call_index == 1:
        assert AdapterDataSource.double_buffer_read_index == 0
        assert result == AdapterDataSource.currentData[0]['data']
    else:
        assert False

def test_sbn_adapter_AdapterDataSource_get_next_when_called_multiple_times_when_new_data_is_true(setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    cut = AdapterDataSource.__new__(AdapterDataSource)
    pre_call_index = AdapterDataSource.double_buffer_read_index
=======
    assert cut.new_data == False
    assert cut.double_buffer_read_index == 1
    assert result == expected_result

def test_sbn_adapter_DataSource_get_next_returns_expected_data_when_new_data_is_true_and_double_buffer_read_index_is_1():
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_get_next_returns_expected_data_when_new_data_is_true_and_double_buffer_read_index_is_1

    # Arrange
    # Renew DataSource to ensure test independence
    cut = DataSource.__new__(DataSource)
    cut.new_data = True
    cut.new_data_lock = MagicMock()
    cut.double_buffer_read_index = 1
    pre_call_index = cut.double_buffer_read_index
    expected_result = MagicMock()
    cut.currentData = []
    cut.currentData.append({'data': expected_result})
    cut.currentData.append({'data': MagicMock()})

    # Act
    result = cut.get_next()

    # Assert
    assert cut.new_data == False
    assert cut.double_buffer_read_index == 0
    assert result == expected_result

def test_sbn_adapter_DataSource_get_next_when_called_multiple_times_when_new_data_is_true():
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_get_next_when_called_multiple_times_when_new_data_is_true
    
    # Arrange
    # Renew DataSource to ensure test independence
    cut = DataSource.__new__(DataSource)
    cut.double_buffer_read_index = pytest.gen.randint(0,1)
    cut.new_data_lock = MagicMock()
    cut.currentData = [MagicMock(), MagicMock()]
    pre_call_index = cut.double_buffer_read_index
    expected_data = []
>>>>>>> c1b3f1d03fa45a6b7b8f96c00999452800972810

    # Act
    results = []
    num_calls = pytest.gen.randint(2,10) # arbitrary, 2 to 10
    for i in range(num_calls):
<<<<<<< HEAD
        AdapterDataSource.new_data = True
        results.append(cut.get_next())

    # Assert
    assert AdapterDataSource.new_data == False
    for i in range(num_calls):
        results[i] = AdapterDataSource.currentData[pre_call_index]['data']
        pre_call_index = (pre_call_index + 1) % 2
    assert AdapterDataSource.double_buffer_read_index == pre_call_index
    
def test_sbn_adapter_AdapterDataSource_get_next_behavior_when_new_data_is_false_then_true(mocker, setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    cut = AdapterDataSource.__new__(AdapterDataSource)
    pre_call_index = AdapterDataSource.double_buffer_read_index
=======
        cut.new_data = True
        fake_new_data = MagicMock()
        if cut.double_buffer_read_index == 0:
            cut.currentData[1] = {'data': fake_new_data}
        else:
            cut.currentData[0] = {'data': fake_new_data}
        expected_data.append(fake_new_data)
        results.append(cut.get_next())

    # Assert
    assert cut.new_data == False
    for i in range(num_calls):
        results[i] = expected_data[i]
    assert cut.double_buffer_read_index == (num_calls + pre_call_index) % 2

def test_sbn_adapter_DataSource_get_next_waits_until_new_data_is_available(mocker):
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_get_next_waits_until_new_data_is_available
    
    # Arrange
    # Renew DataSource to ensure test independence
    cut = DataSource.__new__(DataSource)
    cut.new_data_lock = MagicMock()
    cut.double_buffer_read_index = pytest.gen.randint(0,1)
    pre_call_index = cut.double_buffer_read_index
    expected_result = MagicMock()
    cut.new_data = None
    cut.currentData = []
    if pre_call_index == 0:
        cut.currentData.append({'data': MagicMock()})
        cut.currentData.append({'data': expected_result})
    else:
        cut.currentData.append({'data': expected_result})
        cut.currentData.append({'data': MagicMock()})
>>>>>>> c1b3f1d03fa45a6b7b8f96c00999452800972810

    num_falses = pytest.gen.randint(1, 10)
    side_effect_list = [False] * num_falses
    side_effect_list.append(True)

<<<<<<< HEAD
    AdapterDataSource.new_data = PropertyMock(side_effect=side_effect_list)
=======
    mocker.patch.object(cut, 'has_data', side_effect=side_effect_list)
>>>>>>> c1b3f1d03fa45a6b7b8f96c00999452800972810
    mocker.patch(sbn_adapter.__name__ + '.time.sleep')

    # Act
    result = cut.get_next()

    # Assert
<<<<<<< HEAD
    assert sbn_adapter.time.sleep.call_count == num_falses
    assert AdapterDataSource.new_data == False
    if pre_call_index == 0:
        assert AdapterDataSource.double_buffer_read_index == 1
        assert result == AdapterDataSource.currentData[1]['data']
    elif pre_call_index == 1:
        assert AdapterDataSource.double_buffer_read_index == 0
        assert result == AdapterDataSource.currentData[0]['data']
    else:
        assert False

# tests for AdapterDataSource.has_more
def test_sbn_adapter_AdapterDataSource_has_more_returns_true(setup_teardown):
    # Arrange
    # Renew AdapterDataSource to ensure test independence
    AdapterDataSource = sbn_adapter.AdapterDataSource
    cut = AdapterDataSource.__new__(AdapterDataSource)

    # Act
    result = cut.has_more()

    # Assert
    assert result == True

# sbn_adapter parse_config_data tests
# TODO: parse_meta_data_file implementation is common between sbn_adapter and csv_parser
def test_sbn_adapter_parse_meta_data_file_returns_call_to_extract_meta_data_file_given_metadata_file_when_given_ss_breakdown_does_not_resolve_to_False(mocker, setup_teardown):
    # Arrange
    AdapterDataSource = sbn_adapter.AdapterDataSource
    cut = AdapterDataSource.__new__(AdapterDataSource)

    arg_configFile = MagicMock()
    arg_ss_breakdown = True if pytest.gen.randint(0, 1) else MagicMock()

    expected_result = MagicMock()

    mocker.patch(sbn_adapter.__name__ + '.extract_meta_data', return_value=expected_result)
    mocker.patch(sbn_adapter.__name__ + '.len')

    # Act
    result = cut.parse_meta_data_file(arg_configFile, arg_ss_breakdown)

    assert(False)
    # Assert
    assert sbn_adapter.extract_meta_data.call_count == 1
    assert sbn_adapter.extract_meta_data.call_args_list[0].args == (arg_configFile, )
    assert sbn_adapter.len.call_count == 0
    assert result == expected_result

def test_sbn_adapter_parse_meta_data_file_returns_call_to_extract_meta_data_file_given_metadata_file_set_to_empty_list_when_len_of_call_value_dict_def_of_subsystem_assigments_when_given_ss_breakdown_evaluates_to_False(mocker, setup_teardown):
    # Arrange
    arg_configFile = MagicMock()
    arg_ss_breakdown = False if pytest.gen.randint(0, 1) else 0

    forced_return_extract_meta_data = {}
    forced_return_len = 0
    fake_empty_processed_filepath = MagicMock()
    forced_return_extract_meta_data['subsystem_assignments'] = fake_empty_processed_filepath

    expected_result = []

    mocker.patch(sbn_adapter.__name__ + '.extract_meta_data', return_value=forced_return_extract_meta_data)
    mocker.patch(sbn_adapter.__name__ + '.len', return_value=forced_return_len)

    # Act
    result = pytest.cut.parse_meta_data_file(arg_configFile, arg_ss_breakdown)

    # Assert
    assert sbn_adapter.extract_meta_data.call_count == 1
    assert sbn_adapter.extract_meta_data.call_args_list[0].args == (arg_configFile, )
    assert sbn_adapter.len.call_count == 1
    assert sbn_adapter.len.call_args_list[0].args == (fake_empty_processed_filepath, )
    assert result['subsystem_assignments'] == expected_result

def test_sbn_adapter_parse_meta_data_file_returns_call_to_extract_meta_data_given_metadata_file__with_dict_def_subsystem_assignments_def_of_call_set_to_single_item_list_str_MISSION_for_each_item_when_given_ss_breakdown_evaluates_to_False(mocker, setup_teardown):
    # Arrange
    arg_configFile = MagicMock()
    arg_ss_breakdown = False if pytest.gen.randint(0, 1) else 0

    forced_return_extract_meta_data = {}
    forced_return_process_filepath = MagicMock()
    fake_processed_filepath = []
    num_fake_processed_filepaths = pytest.gen.randint(1,10) # arbitrary, from 1 to 10 (0 has own test)
    for i in range(num_fake_processed_filepaths):
        fake_processed_filepath.append(i)
    forced_return_extract_meta_data['subsystem_assignments'] = fake_processed_filepath
    forced_return_len = num_fake_processed_filepaths

    expected_result = []
    for i in range(num_fake_processed_filepaths):
        expected_result.append(['MISSION'])

    mocker.patch(sbn_adapter.__name__ + '.extract_meta_data', return_value=forced_return_extract_meta_data)
    mocker.patch(sbn_adapter.__name__ + '.len', return_value=forced_return_len)

    # Act
    result = pytest.cut.parse_meta_data_file(arg_configFile, arg_ss_breakdown)

    # Assert
    assert sbn_adapter.extract_meta_data.call_count == 1
    assert sbn_adapter.extract_meta_data.call_args_list[0].args == (arg_configFile, )
    assert sbn_adapter.len.call_count == 1
    assert sbn_adapter.len.call_args_list[0].args == (fake_processed_filepath, )
    assert result['subsystem_assignments'] == expected_result
=======
    assert cut.has_data.call_count == num_falses + 1
    assert sbn_adapter.time.sleep.call_count == num_falses
    assert cut.new_data == False
    if pre_call_index == 0:
        assert cut.double_buffer_read_index == 1
    elif pre_call_index == 1:
        assert cut.double_buffer_read_index == 0
    else:
        assert False

    assert result == expected_result

# has_more tests
def test_sbn_adapter_DataSource_has_more_always_returns_True():
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_has_more_always_returns_True
    cut = DataSource.__new__(DataSource)
    assert cut.has_more() == True

# mesage_listener_thread tests
def test_sbn_adapter_message_listener_thread_calls_get_current_data(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)
    expected_app_name = MagicMock()
    expected_data_struct = MagicMock()
    fake_msg_id = "1234"
    fake_lookup_table = {fake_msg_id: (expected_app_name, expected_data_struct)}
    cut.__setattr__('msgID_lookup_table', fake_lookup_table)

    fake_generic_recv_msg_p = MagicMock()
    fake_generic_recv_msg_p.contents = MagicMock()
    fake_generic_recv_msg_p.contents.TlmHeader.Primary.StreamId = fake_msg_id

    fake_recv_msg_p = MagicMock()
    fake_recv_msg_p.contents = 'not heyy'


    def mock_POINTER_func(struct):
        if struct == sbn_adapter.sbn.sbn_data_generic_t:
            def return_func():
                return fake_generic_recv_msg_p

        elif struct == expected_data_struct:
            def return_func():
                return fake_recv_msg_p
            
        else:
            raise ValueError(f"Unexpected Struct {struct} used.")
        
        return return_func #return pointers wrapped in a function b/c that's how ctypes does it
    
    mocker.patch(sbn_adapter.__name__ + ".POINTER", side_effect = mock_POINTER_func)

    # for exiting the while loop
    intentional_exception = KeyboardInterrupt('[TEST]: Exiting infinite loop')
    mocker.patch.object(cut, 'get_current_data', side_effect = [intentional_exception])

    # Act
    with pytest.raises(KeyboardInterrupt) as e_info:
        cut.message_listener_thread()
    
    # Assert
    assert cut.get_current_data.call_count == 1
    assert fake_recv_msg_p.contents == fake_generic_recv_msg_p.contents
    assert cut.get_current_data.call_args_list
    expected_call = (fake_recv_msg_p.contents, expected_data_struct, expected_app_name)
    assert cut.get_current_data.call_args_list[0].args == expected_call

# get_current_data tests
def test_sbn_adapter_Data_Source_get_current_data_calls_gather_field_names_correctly(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)
    cut.double_buffer_read_index = pytest.gen.randint(0,1)
    n = pytest.gen.randint(1,9)
    cut.currentData =  [{'headers':[f'field_{i}' for i in range(n)],'data':[[0] for x in range(n)]}, 
                        {'headers':[f'field_{i}' for i in range(n)],'data':[[0] for x in range(n)]}]
    cut.new_data_lock = MagicMock()

    arg_recv_msg = MagicMock()
    arg_recv_msg._fields_ = [(MagicMock(), MagicMock()) for x in range(n)]
    arg_recv_msg._fields_.insert(0, 'header')
    arg_recv_msg.TlmHeader.Secondary = MagicMock()
    arg_recv_msg.TlmHeader.Secondary.Seconds = pytest.gen.randint(0,9)
    arg_recv_msg.TlmHeader.Secondary.Subseconds = pytest.gen.randint(0,9)

    arg_data_struct = MagicMock()
    arg_app_name = MagicMock()
    
    mocker.patch.object(cut, 'gather_field_names', return_value = [])

    # Act
    cut.get_current_data(arg_recv_msg, arg_data_struct, arg_app_name)

    # Assert
    assert cut.gather_field_names.call_count == n
    assert len(cut.gather_field_names.call_args_list) == n
    for i in range(n):
        expected_args = arg_recv_msg._fields_[i+1]
        assert cut.gather_field_names.call_args_list[i].args == expected_args

def test_sbn_adapter_DataSource_get_current_data_unpacks_sub_fields_correctly(mocker):
    # Arrange
    cut = DataSource.__new__(DataSource)
    cut.double_buffer_read_index = pytest.gen.randint(0,2)
    cut.new_data_lock = MagicMock()
    cut.new_data = MagicMock()

    #  Message structure & data for 'fake_app'
    arg_app_name = 'fake_app'

    arg_recv_msg = MagicMock()
    arg_recv_msg._fields_ = [("TlmHeader", MagicMock()), ("field1", MagicMock())]
    arg_recv_msg.TlmHeader.Secondary.Seconds = 0
    arg_recv_msg.TlmHeader.Secondary.Subseconds = 1
    arg_recv_msg.field1.temperature = 89
    arg_recv_msg.field1.voltage = 5
    arg_recv_msg.field1.velocity.x = 1
    arg_recv_msg.field1.velocity.y = 2

    fake_field_names = [
        "field1.temperature",
        "field1.voltage",
        "field1.velocity.x",
        "field1.velocity.y"
    ]
    mocker.patch.object(cut, 'gather_field_names', return_value = fake_field_names)

    # initialize double buffer
    cut.__setattr__('currentData', [{'headers':[], 'data': []}, {'headers':[], 'data': []}])
    for x in range(0,2):
        for name in fake_field_names:
            cut.currentData[x]['headers'].append(arg_app_name + '.' + name)
            cut.currentData[x]['data'].append([0])

    expected_data = {'headers':[arg_app_name+'.'+"field1.temperature",
                                arg_app_name+'.'+"field1.voltage",
                                arg_app_name+'.'+"field1.velocity.x",
                                arg_app_name+'.'+"field1.velocity.y"],
                     'data':['89','5','1','2'] }
    
    arg_data_struct = MagicMock()

    # Act
    cut.get_current_data(arg_recv_msg, arg_data_struct, arg_app_name)

    # Assert
    assert cut.currentData[(cut.double_buffer_read_index + 1) %2] == expected_data
    assert cut.new_data == True

# has_data tests
def test_sbn_adapter_DataSource_has_data_returns_instance_new_data():
    # copied from test_redis_adapter.py
    # test_redis_adapter_DataSource_has_data_returns_instance_new_data
    cut = DataSource.__new__(DataSource)
    expected_result = MagicMock()
    cut.new_data = expected_result

    result = cut.has_data()

    assert result == expected_result
>>>>>>> c1b3f1d03fa45a6b7b8f96c00999452800972810
