<?xml version="1.0" encoding="UTF-8"?>
<schema xmlns="http://purl.oclc.org/dsdl/schematron" queryBinding="xslt2">
  <ns prefix="tei" uri="http://www.tei-c.org/ns/1.0"/>
  <pattern id="lex0-header">
    <rule context="tei:TEI">
      <assert test="tei:teiHeader/tei:fileDesc">teiHeader/fileDesc is required</assert>
      <assert test="tei:teiHeader/tei:encodingDesc">teiHeader/encodingDesc is required</assert>
      <assert test="tei:teiHeader/tei:revisionDesc">teiHeader/revisionDesc is required</assert>
    </rule>
  </pattern>
  <pattern id="lex0-entry">
    <rule context="tei:entry">
      <assert test="tei:form[@type='lemma']/tei:orth">entry needs a lemma orth</assert>
      <assert test="tei:sense">entry needs at least one sense</assert>
    </rule>
  </pattern>
  <pattern id="lex0-sense">
    <rule context="tei:sense">
      <assert test="tei:cit[@xml:lang='de']">sense needs a German source cit</assert>
      <assert test="tei:cit[@xml:lang='ru']">sense needs a Russian translation cit</assert>
      <assert test="tei:idno[@type='record_id']">sense needs a record_id</assert>
    </rule>
  </pattern>
</schema>
