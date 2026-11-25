import re
from pathlib import Path
from lxml import etree

DSIG_NS = "http://www.w3.org/2000/09/xmldsig#"


class XmlProcessor:
    def __init__(self, xml_path: Path) -> None:
        self.xml_path = xml_path
        self.tree = self._parse_xml(xml_path)
        self.root = self.tree.getroot()

    @staticmethod
    def _decode_raw_xml(raw_bytes: bytes) -> str:
        if raw_bytes.startswith(b"\xff\xfe") or raw_bytes.startswith(b"\xfe\xff"):
            return raw_bytes.decode("utf-16")
        if raw_bytes.startswith(b"\xef\xbb\xbf"):
            return raw_bytes.decode("utf-8-sig")

        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            pass

        if b"\x00" in raw_bytes:
            for enc in ("utf-16-le", "utf-16-be"):
                try:
                    text = raw_bytes.decode(enc)
                    if "<" in text and ">" in text:
                        return text
                except UnicodeDecodeError:
                    continue

        for enc in ("cp1252", "latin-1"):
            try:
                return raw_bytes.decode(enc)
            except UnicodeDecodeError:
                continue

        return raw_bytes.decode("utf-8", errors="replace")

    @classmethod
    def _parse_xml(cls, xml_path: Path) -> etree._ElementTree:
        parser = etree.XMLParser(remove_blank_text=False)
        raw_bytes = xml_path.read_bytes()

        try:
            return etree.ElementTree(etree.fromstring(raw_bytes, parser=parser))
        except etree.XMLSyntaxError:
            text = cls._decode_raw_xml(raw_bytes)
            normalized_text = re.sub(
                r'(<\?xml\b[^>]*\bencoding=["\'])([^"\']+)(["\'])',
                r"\1utf-8\3",
                text,
                count=1,
                flags=re.IGNORECASE,
            )
            return etree.ElementTree(
                etree.fromstring(normalized_text.encode("utf-8"), parser=parser)
            )

    def _get_correct_chnfe(self) -> str | None:
        tags = self.root.xpath(".//*[local-name()='protNFe']/*[local-name()='infProt']/*[local-name()='chNFe']")
        if not tags or not tags[0].text:
            return None
        chave = re.sub(r"\D", "", tags[0].text)
        return chave or None

    def _replace_chnfe(self) -> None:
        correct_chnfe = self._get_correct_chnfe()
        if not correct_chnfe:
            return

        chave_antiga = ""

        inf_nfe_list = self.root.xpath(".//*[local-name()='infNFe']")
        if inf_nfe_list:
            inf_nfe_tag = inf_nfe_list[0]
            id_atual = inf_nfe_tag.get("Id", "")
            chave_antiga = re.sub(r"\D", "", id_atual)
            if id_atual:
                inf_nfe_tag.set("Id", f"NFe{correct_chnfe}")

        qr_code_list = self.root.xpath(".//*[local-name()='qrCode']")
        if qr_code_list and qr_code_list[0].text and chave_antiga:
            qr_tag = qr_code_list[0]
            if chave_antiga in qr_tag.text:
                qr_tag.text = qr_tag.text.replace(chave_antiga, correct_chnfe, 1)

        ref_list = self.root.xpath(
            ".//*[local-name()='Signature']/*[local-name()='SignedInfo']/*[local-name()='Reference']"
        )
        for reference_tag in ref_list:
            uri_atual = (reference_tag.get("URI") or "").strip()
            if not uri_atual:
                continue

            if uri_atual.startswith("#NFe"):
                reference_tag.set("URI", f"#NFe{correct_chnfe}")
            elif chave_antiga and chave_antiga in uri_atual:
                reference_tag.set("URI", uri_atual.replace(chave_antiga, correct_chnfe, 1))

    def process_xml(self, new_xml_path: Path) -> None:
        self._replace_chnfe()
        self.tree.write(
            str(new_xml_path),
            encoding="utf-8",
            xml_declaration=True,
            pretty_print=False,
        )
