import pytest

from main import YaUploader


def test_get_path_before_post():
    YD = YaUploader()
    status = YD.get_path(path='555555')
    assert status == 404

def test_post_path():
    YD = YaUploader()
    status = YD.post_path(path='555555')
    assert status == 201

def test_get_path():
    YD = YaUploader()
    status = YD.get_path(path='555555')
    assert status == 200

def test_delete_path():
    YD = YaUploader()
    status = YD.delete_path(path='555555')
    assert status == 204

def test_get_path_after_delete():
    YD = YaUploader()
    status = YD.get_path(path='555555')
    assert status == 404