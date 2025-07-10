#!/usr/bin/env python3
"""
Test suite for NDJSON recovery tool
Validates data recovery from concatenated JSON objects
"""

import pytest
import tempfile
import os
import json
from fix_ndjson import fix_ndjson_file, split_concatenated_json


class TestNDJSONRecovery:
    """Test NDJSON recovery functionality"""

    def create_test_file(self, content_lines):
        """Create temporary test file with given content"""
        temp_file = tempfile.NamedTemporaryFile(
            mode="w", delete=False, suffix=".ndjson"
        )
        for line in content_lines:
            temp_file.write(line + "\n")
        temp_file.close()
        return temp_file.name

    def test_valid_ndjson_unchanged(self):
        """Test that valid NDJSON files are not modified"""
        valid_content = [
            '{"sessionguid": "test-1", "sessiontype": "Messaging", "text": "Hello"}',
            '{"sessionguid": "test-2", "sessiontype": "Telephony", "text": "Goodbye"}',
            '{"sessionguid": "test-3", "sessiontype": "Email", "data": {"nested": "value"}}',
        ]

        input_file = self.create_test_file(valid_content)
        output_file = input_file.replace(".ndjson", "_fixed.ndjson")

        try:
            objects_recovered, lines_fixed, total_lines = fix_ndjson_file(
                input_file, output_file
            )

            # Should recover all objects without fixing any lines
            assert objects_recovered == 3
            assert lines_fixed == 0
            assert total_lines == 3

            # Output should be identical to input
            with open(output_file, "r") as f:
                output_lines = [line.strip() for line in f if line.strip()]

            assert len(output_lines) == 3
            for i, line in enumerate(output_lines):
                assert json.loads(line) == json.loads(valid_content[i])

        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_concatenated_objects_recovery(self):
        """Test recovery of concatenated JSON objects"""
        # Simulate the exact error pattern found in production data
        concatenated_content = [
            '{"sessionguid": "test-1", "sessiontype": "Messaging"}{"sessionguid": "test-2", "sessiontype": "Telephony"}',
            '{"sessionguid": "test-3", "sessiontype": "Email", "nested": {"data": "value"}}',
            '{"sessionguid": "test-4", "data": "single"}{"sessionguid": "test-5", "data": "double"}{"sessionguid": "test-6", "data": "triple"}',
        ]

        input_file = self.create_test_file(concatenated_content)
        output_file = input_file.replace(".ndjson", "_fixed.ndjson")

        try:
            objects_recovered, lines_fixed, total_lines = fix_ndjson_file(
                input_file, output_file
            )

            # Should recover 6 objects total, fix 2 lines
            assert objects_recovered == 6
            assert lines_fixed == 2  # Lines 1 and 3 have concatenated objects
            assert total_lines == 3

            # Verify all objects are valid and separate
            with open(output_file, "r") as f:
                output_lines = [line.strip() for line in f if line.strip()]

            assert len(output_lines) == 6

            # Verify specific recovered objects
            objects = [json.loads(line) for line in output_lines]

            # From line 1 (2 objects)
            assert objects[0]["sessionguid"] == "test-1"
            assert objects[1]["sessionguid"] == "test-2"

            # From line 2 (1 object - unchanged)
            assert objects[2]["sessionguid"] == "test-3"

            # From line 3 (3 objects)
            assert objects[3]["sessionguid"] == "test-4"
            assert objects[4]["sessionguid"] == "test-5"
            assert objects[5]["sessionguid"] == "test-6"

        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_split_concatenated_json_simple(self):
        """Test basic concatenated JSON splitting"""
        concatenated = '{"a": 1}{"b": 2}'
        result = split_concatenated_json(concatenated)

        assert len(result) == 2
        assert json.loads(result[0]) == {"a": 1}
        assert json.loads(result[1]) == {"b": 2}

    def test_split_concatenated_json_complex(self):
        """Test complex nested JSON splitting"""
        concatenated = '{"data": {"nested": "value", "array": [1, 2, 3]}, "type": "test"}{"id": "second", "metadata": {"flag": true}}'
        result = split_concatenated_json(concatenated)

        assert len(result) == 2

        first = json.loads(result[0])
        assert first["data"]["nested"] == "value"
        assert first["data"]["array"] == [1, 2, 3]

        second = json.loads(result[1])
        assert second["id"] == "second"
        assert second["metadata"]["flag"] is True

    def test_split_concatenated_json_with_strings_containing_braces(self):
        """Test splitting when JSON strings contain braces"""
        concatenated = '{"text": "Hello {world} how are }you{?", "id": 1}{"text": "Another {message}", "id": 2}'
        result = split_concatenated_json(concatenated)

        assert len(result) == 2

        first = json.loads(result[0])
        assert first["text"] == "Hello {world} how are }you{?"
        assert first["id"] == 1

        second = json.loads(result[1])
        assert second["text"] == "Another {message}"
        assert second["id"] == 2

    def test_single_object_no_split(self):
        """Test that single valid objects are not split"""
        single_object = '{"sessionguid": "test", "data": {"complex": "structure"}}'
        result = split_concatenated_json(single_object)

        assert len(result) == 1
        assert json.loads(result[0]) == json.loads(single_object)

    def test_empty_line_handling(self):
        """Test handling of empty lines and whitespace"""
        content_with_empties = [
            '{"valid": "object"}',
            "",
            "   ",
            '{"another": "object"}{"concatenated": "object"}',
            "",
        ]

        input_file = self.create_test_file(content_with_empties)
        output_file = input_file.replace(".ndjson", "_fixed.ndjson")

        try:
            objects_recovered, lines_fixed, total_lines = fix_ndjson_file(
                input_file, output_file
            )

            assert objects_recovered == 3
            assert lines_fixed == 1
            assert total_lines == 5  # All lines counted, including empty ones

        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_malformed_json_handling(self):
        """Test handling of truly malformed JSON that cannot be recovered"""
        malformed_content = [
            '{"valid": "object"}',
            '{"invalid": "missing_quote}',  # Cannot be recovered
            '{"another": "valid"}{"also": "valid"}',
        ]

        input_file = self.create_test_file(malformed_content)
        output_file = input_file.replace(".ndjson", "_fixed.ndjson")

        try:
            # Should not crash, but should report incomplete recovery
            objects_recovered, lines_fixed, total_lines = fix_ndjson_file(
                input_file, output_file
            )

            # Should recover 3 objects (1 + 0 + 2), fix 2 lines (malformed + concatenated)
            assert objects_recovered == 3
            assert (
                lines_fixed == 2
            )  # Both the malformed line and concatenated line are "fixed"
            assert total_lines == 3

        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)

    def test_large_scale_simulation(self):
        """Simulate large-scale data recovery scenario"""
        # Generate test data similar to production scale
        content = []

        # 98 normal lines
        for i in range(98):
            content.append(
                f'{{"sessionguid": "normal-{i}", "sessiontype": "Messaging", "data": "content"}}'
            )

        # 2 concatenated lines (simulating 0.1% error rate)
        content.append(
            '{"sessionguid": "concat-1", "sessiontype": "Telephony"}{"sessionguid": "concat-2", "sessiontype": "Email"}'
        )
        content.append(
            '{"sessionguid": "concat-3", "sessiontype": "Social"}{"sessionguid": "concat-4", "sessiontype": "Report"}'
        )

        input_file = self.create_test_file(content)
        output_file = input_file.replace(".ndjson", "_fixed.ndjson")

        try:
            objects_recovered, lines_fixed, total_lines = fix_ndjson_file(
                input_file, output_file
            )

            # Should recover 102 objects (98 + 4), fix 2 lines
            assert objects_recovered == 102
            assert lines_fixed == 2
            assert total_lines == 100

            # Verify 100% success rate
            success_rate = (
                objects_recovered / (lines_fixed * 2 + total_lines - lines_fixed)
            ) * 100
            assert success_rate == 100.0

        finally:
            os.unlink(input_file)
            if os.path.exists(output_file):
                os.unlink(output_file)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
