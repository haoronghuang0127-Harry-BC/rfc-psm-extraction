import unittest

from rfc.rfc_types import RfcSegment

from split_experiment.referenced_context_splitting.generate_referenced_context_segments import _build_referenced_context_segment, _build_section_index, _find_section_references


# Check reference ownership without calling Ollama or changing saved experiment data.
class InternalReferenceTests(unittest.TestCase):
    def test_external_prefixes_are_skipped(self) -> None:
        examples: list[str] = ["See [RFC793], Section 3.1.", "See RFC 793's Section 3.", "See RFC 793’s Section 3.", "See RFC 5961 [9], Section 3.", "See RFC 7657 (Sections 5.1, 5.3, and 6) [50].", "See SIP [RFC3261] (in Section 22.4).", "See [35], Section 4.", "See [SASL], Section 7.1."]

        for text in examples:
            with self.subTest(text=text):
                self.assertEqual(_find_section_references(section_text=text, current_rfc="4340"), [])

    def test_external_suffixes_are_skipped(self) -> None:
        examples: list[str] = ["See Section 3.1 of RFC793.", "See Section 4 of the ACE framework [RFC9200].", "See Section 2.3.1 of the base DNS document, RFC 1035 [2].", "See Section 7.1 [SASL].", "See Section 4.7 of MQTT v5.0.", "See Section 4.7 of the MQTT v5.0 OASIS Standard [MQTT-OASIS-Standard-v5].", "See Section 5.3.1.1 of [ISO.8601.2000]."]

        for text in examples:
            with self.subTest(text=text):
                self.assertEqual(_find_section_references(section_text=text, current_rfc="9431"), [])

    def test_current_rfc_is_not_mistaken_for_an_external_document(self) -> None:
        examples: list[str] = ["See Section 8 of RFC 9431.", "See RFC 9431, Section 8.", "See [RFC9431], Section 8.", "See Section 8 [RFC9431].", "See Section 8 of [RFC9431].", "See Section 8 of RFC09431."]

        for text in examples:
            with self.subTest(text=text):
                self.assertEqual(_find_section_references(section_text=text, current_rfc="9431"), ["8"])

    def test_unrelated_rfc_mentions_do_not_remove_internal_references(self) -> None:
        examples: list[str] = ["Unlike RFC8446, see Section 8 for details.", "See Section 8 of this document for comparison with RFC8446.", "See Section 8. RFC8446 describes TLS.", "See Section 8 [Deprecated]."]

        for text in examples:
            with self.subTest(text=text):
                self.assertEqual(_find_section_references(section_text=text, current_rfc="9431"), ["8"])

    def test_owner_after_a_section_range_is_checked(self) -> None:
        for text in ["See Sections 9.3-9.7 of [RFC7231].", "See Sections 9.3 through 9.7 of [RFC7231].", "See Sections 9.3–9.7 of [RFC7231]."]:
            with self.subTest(text=text):
                self.assertEqual(_find_section_references(section_text=text, current_rfc="7826"), [])

    def test_external_appendices_are_skipped(self) -> None:
        self.assertEqual(_find_section_references(section_text="See Appendix A of RFC793 and Appendices B and C of [RFC793].", current_rfc="4340"), [])
        self.assertEqual(_find_section_references(section_text="See Appendix A of this document.", current_rfc="4340"), ["A"])

    def test_external_iso_owner_can_continue_into_the_following_clause(self) -> None:
        text: str = "Use Section 5.3.1.1 of [ISO.8601.2000], allowing decimal fractions following Section 5.3.1.3 requiring a full stop. See Section 4.4 of this document."

        self.assertEqual(_find_section_references(section_text=text, current_rfc="7826"), ["4.4"])

    def test_rfc_quotation_keeps_its_original_owner(self) -> None:
        text: str = "RFC 1122 requires addresses to be validated:\n   |  Ignore an invalid source address (see\n   |  Section 3.2.1.3).\nSee Section 4 of this document."

        self.assertEqual(_find_section_references(section_text=text, current_rfc="9293"), ["4"])
        self.assertEqual(_find_section_references(section_text=text, current_rfc="1122"), ["3.2.1.3", "4"])

    def test_rtsp_abnf_reference_is_internal(self) -> None:
        text: str = "The token is defined by the ABNF [RFC5234] in Section 20."

        self.assertEqual(_find_section_references(section_text=text, current_rfc="7826"), ["20"])

    def test_internal_reference_after_an_external_reference_is_kept(self) -> None:
        text: str = "See [RFC793], Section 3.1. Also see Section 3.1 of this document."

        self.assertEqual(_find_section_references(section_text=text, current_rfc="4340"), ["3.1"])

    def test_external_reference_does_not_append_a_same_numbered_local_section(self) -> None:
        source: dict[str, str] = {"section_number": "9", "section_name": "Source", "tag": "Section 9 Source", "content": "See [RFC793], Section 3.1. Also see Section 4 of this document."}
        local_section: dict[str, str] = {"section_number": "4", "section_name": "Local", "tag": "Section 4 Local", "content": "Local content. See Section 5."}
        wrong_section: dict[str, str] = {"section_number": "3.1", "section_name": "Wrong", "tag": "Section 3.1 Wrong", "content": "Do not append this local section for RFC793."}
        section_index: dict[str, dict[str, str]] = {"3.1": wrong_section, "4": local_section}

        result = _build_referenced_context_segment(segment=source, section_index=section_index, current_rfc="4340")

        self.assertEqual(result["referenced_sections"], ["4"])
        self.assertEqual(result["unresolved_references"], [])
        self.assertTrue(result["content"].startswith(source["content"] + "\n\n<referenced_context>\n"))
        self.assertIn(local_section["content"], result["content"])
        self.assertNotIn(wrong_section["content"], result["content"])
        self.assertEqual(set(result), {"section_number", "section_name", "tag", "content", "referenced_sections", "unresolved_references"})


# Build a small source block for section index tests.
def _build_test_segment(number: str, name: str, content: str) -> RfcSegment:
    return {"section_number": number, "section_name": name, "tag": f"Section {number} {name}", "content": content}


# Check chapter lookup separately from reference ownership.
class SectionIndexTests(unittest.TestCase):
    def test_wrapped_reference_is_not_a_heading(self) -> None:
        source = _build_test_segment("3.", "Operation", "See section\n   3.1.3 for a description of this situation.\n3.1.1. First\n   First body.\n3.1.3. Collision\n   Correct collision body.\n3.2. Next\n   Next body.")

        index = _build_section_index(rfc_segments=[source])

        self.assertEqual(index["3.1.3"]["section_name"], "Collision")
        self.assertEqual(index["3.1.3"]["content"], "3.1.3. Collision\n   Correct collision body.\n")

    def test_wrapped_reference_does_not_cut_a_section_short(self) -> None:
        source = _build_test_segment("3", "Operation", "3.1 First\n   First body.\n3.2 Second\n   See section\n      3.1. This action changes the state.\n   Keep the rest of this paragraph.\n3.3 Third\n   Third body.")

        index = _build_section_index(rfc_segments=[source])

        self.assertIn("Keep the rest of this paragraph.", index["3.2"]["content"])
        self.assertNotIn("Third body.", index["3.2"]["content"])

    def test_hidden_top_level_section_is_found_and_bounds_the_previous_section(self) -> None:
        source = _build_test_segment("25", "Syntax", "Syntax body.\n26 Security Considerations\n   Security introduction.\n26.1 Threats\n   Threat body.")
        following = _build_test_segment("27", "Registries", "Registry body.")

        index = _build_section_index(rfc_segments=[source, following])

        self.assertEqual(index["25"]["content"], "Syntax body.\n")
        self.assertEqual(index["26"]["section_name"], "Security Considerations")
        self.assertIn("Threat body.", index["26"]["content"])
        self.assertNotIn("Registry body.", index["26"]["content"])
        self.assertEqual(index["26.1"]["content"], "26.1 Threats\n   Threat body.")

    def test_hidden_appendices_are_indexed(self) -> None:
        source = _build_test_segment("11", "Security", "Security body.\nAppendix A. Changes\n   Change list.\nA.1 Details\n   Detail body.\nAppendix B. Examples\n   Example body.")

        index = _build_section_index(rfc_segments=[source])

        self.assertEqual(set(index), {"11", "A", "A.1", "B"})
        self.assertEqual(index["11"]["content"], "Security body.\n")
        self.assertIn("Detail body.", index["A"]["content"])
        self.assertNotIn("Example body.", index["A"]["content"])

    def test_ftp_style_indentation_is_preserved(self) -> None:
        source = _build_test_segment("3", "Transfer", "   3.1. DATA\n      Data body.\n      3.1.1. TYPES\n         Type body.\n         3.1.1.1. ASCII\n            ASCII body.\n   3.2. NEXT\n      Next body.")

        index = _build_section_index(rfc_segments=[source])

        self.assertEqual(set(index), {"3", "3.1", "3.1.1", "3.1.1.1", "3.2"})
        self.assertIn("ASCII body.", index["3.1"]["content"])
        self.assertNotIn("Next body.", index["3.1"]["content"])

    def test_numeric_and_punctuation_titles_are_valid(self) -> None:
        source = _build_test_segment("17", "Responses", '17.1. 100 Continue\n   Response body.\n17.2. "Blind" Copies\n   Copy body.\n17.3. #-literals\n   Literal body.')

        index = _build_section_index(rfc_segments=[source])

        self.assertEqual(index["17.1"]["section_name"], "100 Continue")
        self.assertEqual(index["17.2"]["section_name"], '"Blind" Copies')
        self.assertEqual(index["17.3"]["section_name"], "#-literals")

    def test_parent_and_first_child_can_share_a_start_position(self) -> None:
        source = _build_test_segment("3", "Parent", "3.1 Child\n   Complete child body.")

        index = _build_section_index(rfc_segments=[source])

        self.assertEqual(index["3"]["content"], source["content"])
        self.assertEqual(index["3.1"]["content"], source["content"])

    def test_metadata_does_not_duplicate_a_written_heading(self) -> None:
        source = _build_test_segment("3", "Parent", "\n3. Parent\n   Parent body.\n3.1 Child\n   Child body.")

        index = _build_section_index(rfc_segments=[source])

        self.assertEqual(set(index), {"3", "3.1"})
        self.assertIn("Parent body.", index["3"]["content"])

    def test_duplicate_real_heading_numbers_are_not_guessed(self) -> None:
        source = _build_test_segment("3", "Parent", "3.1 First meaning\n   First body.\n3.1 Second meaning\n   Second body.\n3.2 Next\n   Next body.")

        index = _build_section_index(rfc_segments=[source])

        self.assertNotIn("3.1", index)
        self.assertIn("First body.", index["3"]["content"])
        self.assertIn("Second body.", index["3"]["content"])
        self.assertIn("3.2", index)

    def test_roman_appendices_and_unnumbered_boundaries(self) -> None:
        source = _build_test_segment("8", "End", "Main body.\nAPPENDIX I PAGE STRUCTURE\n   Page body.\nAPPENDIX II COMMANDS\n   Command body.")
        copyright_block = _build_test_segment("Full", "Copyright Statement", "Copyright text.")

        index = _build_section_index(rfc_segments=[source, copyright_block])

        self.assertEqual(set(index), {"8", "I", "II"})
        self.assertNotIn("Copyright text.", index["II"]["content"])

    def test_contents_entries_and_addresses_are_not_headings(self) -> None:
        source = _build_test_segment("3", "Parent", "3.1 Child ........ 10\n3.1 Child\n   Real body.\n   5000 Forbes Ave\n   A plain sentence.")

        index = _build_section_index(rfc_segments=[source])

        self.assertEqual(set(index), {"3", "3.1"})
        self.assertEqual(index["3.1"]["section_name"], "Child")

    def test_original_blocks_are_not_modified(self) -> None:
        source = _build_test_segment("3.", "Parent", "3.1 Child\n   Body.")
        original = dict(source)

        _build_section_index(rfc_segments=[source])

        self.assertEqual(source, original)

    def test_existing_section_whitespace_is_preserved(self) -> None:
        source = _build_test_segment("3", "Parent", "\n   Introduction.\n\n3.1 Child\n   Body.\n\n")
        following = _build_test_segment("4", "Next", "Next body.")

        index = _build_section_index(rfc_segments=[source, following])

        self.assertEqual(index["3"]["content"], source["content"])
        self.assertEqual(index["3.1"]["content"], "3.1 Child\n   Body.\n\n")


if __name__ == "__main__":
    unittest.main()
