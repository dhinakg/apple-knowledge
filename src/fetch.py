import base64
import io
import plistlib
import shutil
import subprocess
import zipfile
from pathlib import Path

import pyimg4
import remotezip
import requests

from utils.cache import CACHE_DIR
from parsers import device_tree

CACHE_DIR.mkdir(exist_ok=True)

SESSION = requests.Session()


def url_to_path(url: str):
    return CACHE_DIR / url.replace("https://", "").replace("http://", "")

# Other things to look at:
# iOS 18+ simulator runtimes:
# Either:
# - AEAs (encrypted, DMG)
# - Dev portal DMGs (dev portal auth, DMG)
# - Xcode simulator manifest?
#
# Safari 17+ (PKG)

# urls = [input("Enter URL: ").strip()]
urls = """
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77836/4684F9C7-3F22-41B2-A543-08AAA97B9FEF/iPhone17,2_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77773/01645362-ACAC-4B29-BF73-A5397FA1034A/iPhone17,1_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77804/664EF8A2-96CC-4645-95C7-343955A07EA7/iPhone17,4_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77769/2A2DBD27-47A6-40DB-AEF5-E283454A67E8/iPhone17,3_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77857/26BA8F5E-11C9-4536-AA47-7594A718255A/iPhone16,2_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77896/A68E7F32-80F0-43FB-AD8A-C20893AB5CAC/iPhone16,1_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77927/85D04E15-5154-4A52-B0D9-A46B5208BF8E/iPhone15,5_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77882/4DFC65EC-F5C6-46E2-98B2-08EA0EF36538/iPhone15,4_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77820/C2C42D9F-2124-452E-8777-DC860A9721DB/iPhone15,3_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77778/2D0C56D2-7F47-4346-8397-9BBFA1E1DB9D/iPhone15,2_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77774/2D667682-5D4A-4174-8E59-2EF562C74FB8/iPhone14,6_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77858/62A297DC-162F-4137-B54E-0C4EA300D312/iPhone12,8_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77902/006BF944-4F50-4903-8FBC-E3400E7E13BF/iPhone11,8_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77830/F147504C-7BE4-4206-91FF-D53C5417CE85/iPhone14,8_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77763/45692CFE-88D6-4C42-A3D7-9E666556F26D/iPhone14,7_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77868/E901403D-F82A-40D1-8178-519BF5BD1CD0/iPhone14,3_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77909/92DD1AB7-9AD6-4026-8301-DB738A4F1702/iPhone14,2_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77952/4ADDCFA7-0636-46F8-B232-4D073FCBC840/iPhone14,4_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77790/EA4DEBCC-767C-44DB-8D5A-02430A22648E/iPhone14,5_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77819/DBD19B90-6CA3-44A2-A4EA-D4BD1E89578F/iPhone13,2,iPhone13,3_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77793/537871E5-45A3-482E-AC27-DABBFDEE8D4F/iPhone13,4_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77939/55C38C64-4845-44DB-BFF5-CE167CB40632/iPhone13,1_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77903/E2B9E97C-7082-4B68-ACA2-17E90AA3FDBD/iPhone12,3,iPhone12,5_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77756/9AA40CC8-01BD-4430-9F67-6016EF20A592/iPhone12,1_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77760/D36927A6-81C6-4921-BB99-B3F15FD7ACE3/iPhone11,2,iPhone11,4,iPhone11,6_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77826/5D5C3C17-3CD5-42DC-A787-D49BFD7A14A1/iPad_Fall_2021_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77875/EA45DF27-72CE-462F-9540-FAD9C847D2C1/iPad_Spring_2019_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77782/5C61EC6D-2816-46C0-A77A-C20EFFAFBEC1/iPad_Pro_M4_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77767/7B457CF0-FD00-4B32-97FA-F67B64FED1CA/iPad14,3,iPad14,4,iPad14,5,iPad14,6_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77949/1250B639-2A9F-45FE-9E58-71AE9A20449A/iPad_Pro_Spring_2021_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77809/8D713529-DC52-41F1-BDD5-565D294B1667/iPad_Pro_A12X_A12Z_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77862/C5D4DB51-2B71-4C34-A179-D1C2B3D5A7D9/iPad_Air_M2_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77810/DF15A161-2D95-4FBE-8D31-7B907BA0BDD2/iPad_Spring_2022_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77842/895905A1-B56F-4FE9-BBF9-DD1FD919A245/iPad_Fall_2020_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77904/47AC1B73-71E3-470A-98D8-76E7429AAF09/iPad_10.2_2021_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77879/19143C6F-1508-4904-B3F9-BE23ACC265A4/iPad_10.2_2020_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77845/A97DA5B9-0E5C-45DC-8860-C54B44E928E3/iPad_10.2_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-77892/97356B71-1DD1-4C12-9D2B-B7AD96FA8525/iPad_Fall_2022_18.0_22A3354_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79065/5EA66C39-7D61-4C58-92BD-BBE18D2E2913/iPhone16,2_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78878/B8001671-5BAE-49BB-808E-4F399454CE8D/iPhone16,1_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78882/852A1281-141C-4A24-9105-78733F23B651/iPhone15,5_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78954/8A879FCE-CD96-4FEB-BAFB-0FF58CCB5058/iPhone15,4_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78853/E6FFD79D-6F5D-487A-A84E-1C6E91CEC0A8/iPhone15,3_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79094/90CE304F-6C16-402E-96C9-89260D93CA82/iPhone15,2_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79092/3B7E217F-B59B-4FBB-B682-A1154B0B7039/iPhone14,6_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78884/388F9385-8AF0-43A5-9E5E-D5DB4D171296/iPhone12,8_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79020/99513170-4693-44A2-8D10-3DDCDC053B51/iPhone11,8_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79100/10B26D91-BFFA-4546-8CE9-CF779233BECA/iPhone14,8_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79084/85A17F77-51CF-460C-B384-974D65C19C65/iPhone14,7_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78845/4FCA59A2-2597-4B14-8C88-4F7D612E40B9/iPhone14,3_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79095/E232F560-BF65-49C3-95F4-EACFCADDC3DB/iPhone14,2_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78869/0F0F6579-CDE6-44EB-B3D3-B5E9B9A63649/iPhone14,4_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78847/352B072E-B1C2-4276-AF02-AF854E5F4EA8/iPhone14,5_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79093/CAFF81F3-A128-481C-A7FB-16D0486BCEED/iPhone13,2,iPhone13,3_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79149/EEFC0717-EEEC-4B29-97AF-153A80C4C50B/iPhone13,4_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78924/B233CE63-5984-4480-AEC3-CA367761BD9F/iPhone13,1_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79021/D1C2EDBF-4F40-407A-B2C5-C0D92E0FA251/iPhone12,3,iPhone12,5_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78994/7B1C92E8-587E-4F7E-BB51-1DCADA45517B/iPhone12,1_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79002/2CDE0E28-284D-4554-A20B-DAFB4703AF3F/iPhone11,2,iPhone11,4,iPhone11,6_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78975/859EE38D-06D5-4145-BA62-868C1159E977/iPad_Fall_2021_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79147/8316127F-A6C8-4610-BD31-EC501B61A730/iPad_Spring_2019_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79056/5E0341B9-CAAA-4AE9-B4B0-1D061631CC58/iPad_Pro_M4_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78991/977640C8-F48D-4803-9002-3C94B630B6A2/iPad14,3,iPad14,4,iPad14,5,iPad14,6_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78902/692F54D3-781E-44B1-B158-204017425738/iPad_Pro_Spring_2021_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79132/085EBCE2-A518-4CF1-A7D1-2B4A5BAD8E80/iPad_Pro_A12X_A12Z_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79162/2BF98484-9B71-4DCA-9957-68C168DBF85D/iPad_Pro_HFR_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78977/645A2C98-F6CA-4670-B528-83174BD6C56A/iPad_Air_M2_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78905/4162C120-710C-4628-983B-EF44C8A58B2A/iPad_Spring_2022_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78903/405F7A7B-CEC7-412C-9162-200631208906/iPad_Fall_2020_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78879/D7109076-8FCF-49A0-8C48-CCEE0A0078F5/iPad_10.2_2021_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79160/07931094-4037-404A-BEF1-FB55A72838B3/iPad_10.2_2020_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78914/A081E8C4-D00A-4FC5-A650-A42EA1726236/iPad_10.2_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78995/AE33744E-AF74-4486-9C78-56519F307FDB/iPad_64bit_TouchID_ASTC_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-79061/F30206D9-DECC-44B0-8181-19516E4A15EE/iPad_Fall_2022_17.7_21H16_Restore.ipsw
https://updates.cdn-apple.com/2024SpringFCS/fullrestores/062-47894/28C6D3CB-F9DF-4839-B3BB-E7CA850CEB80/iPhone10,3,iPhone10,6_16.7.10_20H350_Restore.ipsw
https://updates.cdn-apple.com/2024SpringFCS/fullrestores/062-47978/A55BB379-12EA-4097-8517-ED458FCCA70F/iPhone_4.7_P3_16.7.10_20H350_Restore.ipsw
https://updates.cdn-apple.com/2024SpringFCS/fullrestores/062-48167/FAB38851-AFA0-41AA-8C49-6823A9D71D94/iPhone_5.5_P3_16.7.10_20H350_Restore.ipsw
https://updates.cdn-apple.com/2024SpringFCS/fullrestores/062-47994/648C3494-E3C2-49DD-A0AE-7D3BBA4CEF4C/iPadPro_9.7_16.7.10_20H350_Restore.ipsw
https://updates.cdn-apple.com/2024SpringFCS/fullrestores/062-47901/EF726AB4-CA14-4240-AFAD-775375B060A0/iPadPro_12.9_16.7.10_20H350_Restore.ipsw
https://updates.cdn-apple.com/2024SpringFCS/fullrestores/062-47889/FBBD9227-79D6-4FAA-91B9-D20E087BE0E7/iPad_64bit_TouchID_ASTC_16.7.10_20H350_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-43964/EBACFED5-5923-4878-B426-897C6DD6C536/iPhone15,3_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44327/EDD9D5D2-E1C0-4B64-B6B1-642E087BB595/iPhone15,2_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44179/225BC44F-AA2E-4430-B737-890F98535326/iPhone14,6_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44058/662C9F71-4560-49A3-B880-38DD8FC01315/iPhone12,8_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44565/1C53F13B-4BE3-47E1-8C34-628F144EA33A/iPhone14,8_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44329/17C4DE84-C4BB-492B-AE32-AA9D84354BB7/iPhone14,7_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44353/F47B56BF-1C4C-4038-8A78-312B59A7AB12/iPhone14,3_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44704/38923EAD-BEDE-4A31-B13E-D6BF299B7711/iPhone14,2_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44714/82142DF1-6B80-4072-978D-4E097B16BD8D/iPhone14,4_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44383/4156E96A-8EA8-42F1-9FB3-9096AE95B12E/iPhone14,5_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44333/030B0E96-8C6E-4EED-BD1B-3BB467E7D8E3/iPhone13,2,iPhone13,3_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-43876/2C3F20C0-E72A-415D-BC63-33129BABC356/iPhone13,4_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44699/68AF5EA3-F65A-4080-BE81-1267A5A4E3DE/iPhone12,1_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44589/2ABC4B85-F23E-4ADB-8D80-1510A87D7BD8/iPhone11,8_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44665/8F6239BA-C5C7-4C99-BDD8-B03079BBA18F/iPhone13,1_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44509/96D12947-B55B-44BB-BFA7-9231902A4A2B/iPhone12,3,iPhone12,5_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-43832/D00DE3E3-6FAA-4DAA-B17D-94CEF1B5CA1C/iPhone11,2,iPhone11,4,iPhone11,6_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44442/3E93EA1C-5D88-46EF-B954-E56AE59C86F6/iPhone10,3,iPhone10,6_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-43931/986016B7-AA6B-4745-8758-A53D80C16E0D/iPhone_4.7_P3_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44608/A7EDB45C-7089-455F-94F4-B34285DCB33F/iPhone_5.5_P3_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44410/90DC2BF6-99CF-4393-89F6-B97332806D9B/iPad_Fall_2021_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44566/EAC342DA-468C-46C9-A595-180304491598/iPad_Spring_2019_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44752/2F5B228B-9264-4D50-8635-E8B1C85967D3/iPad14,3,iPad14,4,iPad14,5,iPad14,6_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-43918/DBF68648-C000-49DF-BB3C-E2BD94427726/iPad_Pro_Spring_2021_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44203/03798F2B-E74B-439A-8F08-77DB3AF43691/iPad_Pro_A12X_A12Z_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44385/366890C4-D9B5-4938-B399-C19FB58DBEE0/iPad_Pro_HFR_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44733/3E96FD63-87DE-4444-88A9-AC8825327227/iPadPro_9.7_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44119/19735D50-7E1B-4D4D-9059-3616FA451403/iPadPro_12.9_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-43796/8D36D83D-C210-41B9-9BD9-FAB278C2D7DC/iPad_Spring_2022_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44527/AE4D1B09-960F-4A30-A56F-CB0A7D1E2276/iPad_Fall_2020_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-43786/9BCDAE8E-ED9F-439E-8C3B-BFEA3D31C614/iPad_10.2_2021_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44697/34AA3C11-AC7A-48B7-9CF5-0988D591EEDB/iPad_10.2_2020_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44571/B4A5346C-A13B-41EA-8F0D-B3379DABFE22/iPad_10.2_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44669/F4841BD5-CCCB-4678-B402-64EBC3C8BB86/iPad_64bit_TouchID_ASTC_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/042-44828/B9CCAD2E-1D12-4786-8994-068137632CDA/iPad_Fall_2022_16.6.1_20G81_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/062-25155/A0635048-A8BF-4A5B-A8B7-0A1E2F178206/iPodtouch_7_15.8.3_19H386_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/062-24903/5978A6A8-A355-478E-A969-3214E3CC952B/iPhone_4.7_P3_15.8.3_19H386_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/062-24958/6D3A7DA6-3D8C-4A2B-A70D-2996D06A8930/iPhone_5.5_P3_15.8.3_19H386_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/062-25082/E4BE9251-A41C-4788-B473-493D032D8860/iPhone_4.0_64bit_15.8.3_19H386_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/062-25178/530FCCC8-8385-4745-928A-B0BD0200EC3E/iPhone_5.5_15.8.3_19H386_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/062-25146/4885A2FB-8AE2-4D39-9A85-35C4B2BDE22C/iPhone_4.7_15.8.3_19H386_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/062-25002/E11066E3-41E6-427D-B452-72D0A355C4E5/iPad_64bit_TouchID_15.8.3_19H386_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39095/C790F618-F409-4C41-B39B-F29B2168B4AC/iPodtouch_7_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39075/35F20D27-F3D5-442A-8F4C-EFC3915F2EDD/iPhone14,6_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38949/41BC868E-7BEC-4B46-9943-D16648458A65/iPhone11,8,iPhone12,1_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38989/A7D49452-9B91-4E2E-9325-64AEA778972E/iPhone14,3_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39023/4003229C-E504-4FEC-BD31-130A5D569CA7/iPhone14,2_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38864/4F3FAFAC-8BD4-4D43-AE75-CD78E7628C48/iPhone13,2,iPhone13,3_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38946/A9832DD4-C25D-43BC-ACF9-1A28C09A8A4B/iPhone13,4_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38875/5A92883D-5232-4509-95E1-D9117CB65AE1/iPhone12,8_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39060/01E3CC4D-D9D5-4FD8-9D09-FCFE99256FC2/iPhone13,1_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39115/DC104483-B40D-4B77-BA44-FE689BF9A8B1/iPhone11,2,iPhone11,4,iPhone11,6,iPhone12,3,iPhone12,5_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39067/20ACC1A5-8816-484B-A176-DB3A54B16299/iPhone10,3,iPhone10,6_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38914/C7764173-5CC4-4D58-8F8B-F093F9A060F0/iPhone_4.7_P3_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38894/94B29539-E9B4-4288-B79B-957D8A074982/iPhone_5.5_P3_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39072/BFDAFD43-D3FF-4811-B210-6A104D91A201/iPhone_4.0_64bit_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39102/8B9B6001-92E2-49EC-969C-1E2BADF5602D/iPhone_5.5_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39051/60D8E589-3C30-4416-BEA9-2156217142BC/iPhone_4.7_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38985/6F0E9F60-0CE9-4AD1-A029-87157AF44C33/iPhone14,4_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39016/4FCF4672-8B76-45B3-AD09-38794781059C/iPhone14,5_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39093/5D048B6A-287D-46D1-9946-BB499AFEF225/iPad_Fall_2021_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38901/5D706FD1-51E0-4827-B021-D49DE21D0300/iPad_Spring_2019_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39076/45719613-AE30-429D-8F8F-011022F33E7F/iPad_64bit_TouchID_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38938/FA54882E-287C-48C7-9BAF-B2D3B458AA9B/iPad_Pro_Spring_2021_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38943/6E015133-988D-4FB5-9DEE-D46125C37479/iPad_Pro_A12X_A12Z_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39107/9B6073BC-F1FD-4249-A0D2-0600474FC60B/iPad_Pro_HFR_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38916/F33346BE-2B54-44EF-81A4-8F6733C62490/iPadPro_9.7_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38906/7EC0E81E-BA37-453F-9100-E2506D2059AF/iPadPro_12.9_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39002/DC6A4935-518D-44C6-81C4-27196AC25500/iPad_Spring_2022_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38899/2630B75A-D083-4518-AC41-6ADA2C7FD42A/iPad_Fall_2020_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38910/7C7E9AFB-4DFF-4F2C-849B-FF3A76A9A894/iPad_10.2_2021_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39017/9AB64EB2-F037-4AB0-9C91-76071F0B8712/iPad_10.2_2020_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-39024/8675E26F-1C8F-44AC-8F04-47DF24EB7512/iPad_10.2_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2022FallFCS/fullrestores/012-38966/80B885FC-7186-4C64-9E7F-4DA8F1A7E12C/iPad_64bit_TouchID_ASTC_15.7_19H12_Restore.ipsw
https://updates.cdn-apple.com/2021FCSFall/patches/002-26145/25B2492A-FA98-42F6-B892-C2F3038A4CC0/com_apple_MobileAsset_SoftwareUpdate/8c1f55239f2f56f4abdb1714bd6a052b291ac3ab.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26118/375017A4-A9DA-4235-8056-FCB9FB4BF665/com_apple_MobileAsset_SoftwareUpdate/318f6fb6a1ed1d45099b88cccda79430daa4ba15.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26409/F9D0F395-C6B3-439C-BC03-EE95512EA9F5/com_apple_MobileAsset_SoftwareUpdate/0a0ae99d543b9cde43d28206b9135723e021a924.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26274/92A1ED9D-2A7E-4306-8F80-4C4C42012F4A/com_apple_MobileAsset_SoftwareUpdate/a449e0427edcb2e387798c620bb856f36b6abbd3.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26147/DAE06D10-939B-4A44-9FCD-856CBF9051E2/com_apple_MobileAsset_SoftwareUpdate/c7e9563d8267cfd8f4de2ef2b21bcf895c46d3a2.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26264/604C7E21-C184-453B-86CC-FD3010034CBC/com_apple_MobileAsset_SoftwareUpdate/1559d6950a1d914fa0642765ebe3b5dbbc582f70.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26363/F48F45A8-3315-471A-89BC-09565F62B6F9/com_apple_MobileAsset_SoftwareUpdate/5d44bfb0cb1cf63b8bc52b5cbc286a9f9806942b.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26237/DF3D1C59-3BEB-4222-BA16-3B60141B5C3F/com_apple_MobileAsset_SoftwareUpdate/22b1ec54eb254096534bd1580ddf17108f5e7546.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26149/E52688A4-88B6-4C1A-8238-7E7FD28C9426/com_apple_MobileAsset_SoftwareUpdate/30318181ca8fdf977551881dedd1835bb11556dd.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26293/B693C0C8-BAC7-4B80-8BF3-58C18D08EFB1/com_apple_MobileAsset_SoftwareUpdate/a56363fc87d6da2c5ee4a010c4f3cfad1ff4fe22.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26184/CC6A84DB-A8C4-4B45-8918-BD99911B1B36/com_apple_MobileAsset_SoftwareUpdate/e2e94ad971ae3bf8c1d6256163b79966095f8b03.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26360/D7F0DBDC-7BEA-415A-B5F8-986981A49004/com_apple_MobileAsset_SoftwareUpdate/fedde1a256459c5d54d11bf62323acb3d86e1c5b.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26358/A441B5B1-9630-4993-BA8C-38C088403C13/com_apple_MobileAsset_SoftwareUpdate/b064c19b859e7c85cf4bc9a6ca4fc5f4d6793189.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26199/09D99FC0-6A35-4111-BD17-056DD3E5F87C/com_apple_MobileAsset_SoftwareUpdate/be45349523acb4b4a46e347feac0b76df6db6d40.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26128/BA59D1C0-C4E4-48F9-A78E-F13E01F67B5D/com_apple_MobileAsset_SoftwareUpdate/5e5364d5b984b5911b37c7091951151753ebd432.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26141/8C6F95F0-049C-4FDE-A422-20B74378DF30/com_apple_MobileAsset_SoftwareUpdate/a3cbce513d9aa0a32bfb4b328d7e857642d90d36.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26353/D4CA2EDA-78EA-4B0D-8F81-E32FCC07D1CD/com_apple_MobileAsset_SoftwareUpdate/d112c03cbfd38e7e75d17f21c45a80d34d3a055f.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26182/9C4F0D0A-3437-4856-8A81-C46650BBA437/com_apple_MobileAsset_SoftwareUpdate/b2dc04988af8dcd927aa0908f3fc7b6be6acd377.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26214/42C0ED10-27A2-4118-AE9F-B3CFFB66CDD7/com_apple_MobileAsset_SoftwareUpdate/0799a53d05a162182dbf10cf8765413299cb4eff.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26263/25727040-CEF1-4E18-A625-1A8E85F9389C/com_apple_MobileAsset_SoftwareUpdate/2f365707fe04dbf8c6d431897086d668bc770556.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26322/A3FBA6D1-BE3F-4A86-A851-40E5C716E25C/com_apple_MobileAsset_SoftwareUpdate/154efd8b093c1a307f0080224a5187fe73e523a5.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26269/4D45A70E-BFE4-41F1-9D08-E6E54FF19CF0/com_apple_MobileAsset_SoftwareUpdate/1c61a5cbbd51790fb183e25a084b4d48cea107a2.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26356/4A94BC1E-3941-445B-A72A-09CBC97085FD/com_apple_MobileAsset_SoftwareUpdate/f496d919b8af4efa065692bccec548ba14551305.zip
https://updates.cdn-apple.com/2021FCSFall/patches/002-26169/8D819FF2-326E-4E05-AC30-CE4C6D16ABED/com_apple_MobileAsset_SoftwareUpdate/471b479ee89eeefebc8fd12c16d4bc1277c80a23.zip
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44788/B5644920-829A-4CAC-AEA7-5F1D7408FB8F/iPodtouch_7_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45010/CDC675AA-ACD7-4D29-B01A-73C666942252/iPhone13,2,iPhone13,3_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44991/AC0B5B9D-970F-4193-ABD1-D7D5ECAC89A7/iPhone13,4_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45316/E379EE23-B364-4F8F-846E-30A5D865C323/iPhone12,8_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44926/F9B5BAD7-D09B-4F33-B79F-9103C47C6E4E/iPhone11,8,iPhone12,1_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45398/BD943945-88FB-4847-9AF3-E2A6434036DF/iPhone13,1_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45389/0BCEC735-6E9A-464D-8AA7-5263C0F339B4/iPhone11,2,iPhone11,4,iPhone11,6,iPhone12,3,iPhone12,5_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44837/2C953DB8-34A1-4AB0-AF90-1A94045A159F/iPhone10,3,iPhone10,6_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45307/56662841-0D2D-4F77-A7F3-D0D8B1061625/iPhone_4.7_P3_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45254/139E01C7-818F-4FBA-84FC-B8BB92F4BAE5/iPhone_5.5_P3_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44996/F03CD26A-5B14-4FC3-9644-A21D2AA2A12E/iPhone_4.0_64bit_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45094/0FDE655F-00CE-4E74-BCFB-B23429391237/iPhone_5.5_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45224/8DA86D5E-6588-4E37-BCA0-C3B1570D5C92/iPhone_4.7_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44957/95BE8A24-9E10-4484-BED5-1BF4376BB578/iPad_Spring_2019_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44869/978C2F2E-814F-4B6B-BFAF-72DE0247BDC5/iPad_64bit_TouchID_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44854/05759551-AD64-4D90-8232-799D7912AC24/iPad_Pro_Spring_2021_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44966/2EA0220B-AA7C-43EC-8E7D-C5A37BEA8C99/iPad_Pro_A12X_A12Z_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45038/19CEC376-DDB6-493B-B643-4B963E135421/iPad_Pro_HFR_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-44827/EB1E8257-5303-43CC-8F06-3F567A2E812C/iPadPro_9.7_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45138/9FF6545A-6BD6-4421-BAEB-6DF0763E23E1/iPadPro_12.9_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45334/20FC9D85-2A43-4FC8-B6E2-CD2CEEAC98FC/iPad_Fall_2020_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45045/3013C514-EF8E-4EE8-B93B-29BDAF5444CC/iPad_Educational_2020_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45051/A5E8B67F-6171-4BB8-B411-0835CA54956E/iPad_Educational_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2021SpringFCS/fullrestores/071-45423/43CEBAED-3ADA-4615-899A-C4FF6081416F/iPad_64bit_TouchID_ASTC_14.6_18F72_Restore.ipsw
https://updates.cdn-apple.com/2020FallFCS/fullrestores/001-79706/93A4C43C-2B45-47AF-84EA-794F8886B85C/UniversalMac_11.0.1_20B29_Restore.ipsw
https://updates.cdn-apple.com/2022SpringFCS/fullrestores/012-17781/F045A95A-44B4-4BA9-8A8A-919ECCA2BB31/UniversalMac_12.4_21F2081_Restore.ipsw
https://updates.cdn-apple.com/2021FallFCS/fullrestores/071-97388/C361BF5E-0E01-47E5-8D30-5990BC3C9E29/UniversalMac_11.6_20G165_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/042-78241/B45074EB-2891-4C05-BCA4-7463F3AC0982/UniversalMac_14.3_23D56_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-78489/BDA44327-C79E-4608-A7E0-455A7E91911F/UniversalMac_15.0_24A335_Restore.ipsw
https://appledb.dev/device/identifier/Watch7,5
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70402/D504A1BF-0A4C-486E-B10F-B967E5475002/com_apple_MobileAsset_SoftwareUpdate/6091772365f87814095ebcef60254a31569251ad.zip
https://appledb.dev/device/Apple-Watch-Series-9
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70341/3B80A79C-CE43-473C-AA6B-633EC9473653/com_apple_MobileAsset_SoftwareUpdate/84b34834d677d0ebaa166bfab9413190bc20f417.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70575/FED4A247-13E0-4D66-9307-15F4B705CDFA/com_apple_MobileAsset_SoftwareUpdate/e5907cde8fd4e5a146f8f8415ac04e33987a9d30.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70391/F875E442-B69A-41D2-B1E6-BE4907AEB8D6/com_apple_MobileAsset_SoftwareUpdate/b74f6ddd2aba45ba6ef081c111f4e1b3923fa4f1.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70374/8B660067-2458-4111-A734-87BBCB03AF71/com_apple_MobileAsset_SoftwareUpdate/57876351d91ce2ea4a39ed61c64d4cc6022ae59d.zip
https://appledb.dev/device/identifier/Watch6,18
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70455/52EFF25C-669F-48F9-ABCC-0E45670488E8/com_apple_MobileAsset_SoftwareUpdate/e39fc786e88f113865045ebae925a73670d5f9d8.zip
https://appledb.dev/device/Apple-Watch-Series-8
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70330/43AFADB1-C248-4EAB-AD37-F217DBD4EE9F/com_apple_MobileAsset_SoftwareUpdate/f9cb12eeafd294579c1674f506ff0066137f8847.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70582/9F85DF61-4667-4CD6-A71B-617A71DE9A7B/com_apple_MobileAsset_SoftwareUpdate/4b8400107f23c164fceaa97382cbf43a7d949748.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70425/BBF86432-7CCF-4051-827C-DD848F0ABE0A/com_apple_MobileAsset_SoftwareUpdate/d2aa24b471cdefd5b1cf1e0de8ed7200e1b723b5.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70440/3179F9DB-79F1-4CAE-9A00-1918E9D28BBA/com_apple_MobileAsset_SoftwareUpdate/5d33d0f51abd708a7feab6437428d34b82dcfc2d.zip
https://appledb.dev/device/Apple-Watch-SE-(2nd-generation)
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70438/27AE5865-A916-4BEC-9580-083E96A07262/com_apple_MobileAsset_SoftwareUpdate/9b3185c44279c5ccba3ce5f8a28ae65453182a09.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70487/9F5C0412-59A5-43D5-92EA-B320D2366BCE/com_apple_MobileAsset_SoftwareUpdate/a6d9acb5bb2d67b1117e047adf517d5ebc23b438.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70379/CFFB93E2-1DAE-41EA-BF4F-E06677402353/com_apple_MobileAsset_SoftwareUpdate/551ca8c1842fe52da34f63533d42ace7fc4d7635.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70558/1F2456F3-27A2-42E5-AAF8-E9ECFDEA8BEE/com_apple_MobileAsset_SoftwareUpdate/14efd626ef4255061fbdae9da061399a849e045a.zip
https://appledb.dev/device/Apple-Watch-Series-7
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70559/921CC02F-BFE1-4E19-A071-F1DF47AE9FAC/com_apple_MobileAsset_SoftwareUpdate/4b1b3d67ca9ff6f7410d6418df3160683a89718c.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70480/7E8572CA-83EF-4455-9BA0-DE316282AEAF/com_apple_MobileAsset_SoftwareUpdate/1aa168b1fcc93eba95a9924961b732f4421b8ec1.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70365/148AD947-ECBD-4E12-BB76-F12F22FFF198/com_apple_MobileAsset_SoftwareUpdate/865ed5db3822ced8be15a0a197b20048a4adbdf9.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70459/B651D3A0-9263-432D-8C95-7EDA56F29C8D/com_apple_MobileAsset_SoftwareUpdate/8fa3f70b5fde43459b0038d28402370a3d4543d1.zip
https://appledb.dev/device/Apple-Watch-Series-6
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70439/861251AD-F895-48CF-9ED9-6AF6F44EF4F5/com_apple_MobileAsset_SoftwareUpdate/af145ac25b1915cb1d8627c987099a51121258c3.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70518/7B8009D1-C356-4E2D-BC53-F38E52360A5D/com_apple_MobileAsset_SoftwareUpdate/8e995a41b58ccbc42c2f343afcedfd057260325a.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70572/3A31275C-F253-4EEE-8E39-862764ED8514/com_apple_MobileAsset_SoftwareUpdate/ed613efee0447dd5201c996c1738d21c71417d56.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70349/C24220F5-28E3-4DEA-9F68-37B4C7876182/com_apple_MobileAsset_SoftwareUpdate/6556e4b9d48eaaff563aa02a2d3eb76b91874cca.zip
https://appledb.dev/device/Apple-Watch-SE-(1st-generation)
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70418/FC809F20-3CC1-4BC0-AD39-6E1F7ADA980F/com_apple_MobileAsset_SoftwareUpdate/dc9417af27d056b0bdd1d1ba38878615236422e8.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70584/8203C835-5D97-4AC4-8C61-32BE06D3F65E/com_apple_MobileAsset_SoftwareUpdate/908461464c7d872a9e4316d50f228b6555b0115f.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70573/DA85F841-09B9-42F0-8825-DFBB5518DAA6/com_apple_MobileAsset_SoftwareUpdate/cfc072474bb96161755e36f0c52056fb26cb3607.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70467/B2E998BF-8AF7-4BC1-8990-63FA83E47ED1/com_apple_MobileAsset_SoftwareUpdate/27ca16082a54f5bdac640df68b57b856825b8756.zip
https://appledb.dev/device/Apple-Watch-Series-5
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70537/29015960-257F-4157-9E67-6600711DCDEA/com_apple_MobileAsset_SoftwareUpdate/82387615d7b342219c9031651685cf8a24711f07.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70337/96DE3E62-7B83-475E-BDCD-CB76D29CB643/com_apple_MobileAsset_SoftwareUpdate/1117ccb2515bb0c822e8b950641094b8d0c1ee8a.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70478/BBA9A241-DE4F-4B7B-824C-FB14D6EDA177/com_apple_MobileAsset_SoftwareUpdate/db2d4926fea6b7b2ab2b8bb25081e393f45162de.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70513/BCE09153-8DCD-4F0E-A2E7-F05A47ABA2AD/com_apple_MobileAsset_SoftwareUpdate/de2924d8e10ec6e62bee72518465d5911c7735b9.zip
https://appledb.dev/device/Apple-Watch-Series-4
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70388/DA0B5635-EDB6-4F56-9D4D-D5C4AFEC574C/com_apple_MobileAsset_SoftwareUpdate/7777c951e8a54ddd034e34d79cdce64a3cd3a8d7.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70458/8DD88C2B-82F3-4B3C-8631-86AF78F32B0B/com_apple_MobileAsset_SoftwareUpdate/5a9f1cbe2551000d5727d0084638042f8349ee29.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70395/94D73FA9-C8F4-4903-8D03-2F7A954A41E1/com_apple_MobileAsset_SoftwareUpdate/637ff64bf21e81a81238f999790408af8cace9df.zip
https://updates.cdn-apple.com/2024WinterFCS/patches/032-70548/D8146077-C607-4B32-B40F-0D0BFEE7CA7B/com_apple_MobileAsset_SoftwareUpdate/448ae5cccc94e6f3f14f95191b39b512fd0f4031.zip
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/052-63601/2D7183DF-BE7B-4F3B-A57E-A49976203208/Apple_Vision_Pro_1.1_21O211_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-84807/793ED505-7AE5-426F-AA64-685A603923EC/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_9.0_22P353_Restore.ipsw
https://updates.cdn-apple.com/2024SummerFCS/fullrestores/052-69288/FB1A896F-8FD5-4883-A4AF-2C7132A982A5/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_8.6_21P6074_Restore.ipsw
https://updates.cdn-apple.com/2023SpringFCS/fullrestores/052-32649/56AA20CF-E91F-496C-9C6D-4A5E2DC8E89E/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_8.5_21P5077_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/032-50535/98918E72-E9A3-426F-90E8-B09FD290A918/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_8.4_21P4222_Restore.ipsw
https://updates.cdn-apple.com/2024WinterFCS/fullrestores/042-80259/985A1643-93CC-4A13-AEF0-3D84CB095558/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_8.3_21P3049_Restore.ipsw
https://updates.cdn-apple.com/2023FallFCS/fullrestores/042-38594/710CDE6E-D9E7-42E9-A6E2-85722491DEF7/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_8.2_21P2057_Restore.ipsw
https://updates.cdn-apple.com/2023FallFCS/fullrestores/042-11544/3A0CC548-5714-461B-9053-AE977E611005/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_8.1_21P1069_Restore.ipsw
https://updates.cdn-apple.com/2023FallFCS/fullrestores/002-79134/C610C25D-4D8E-45FF-9A4D-38AFFFB2C87F/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_8.0_21P365_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/032-65293/559A69FB-8256-425D-8CA7-E9E0C769E736/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_7.6_20P6072_Restore.ipsw
https://updates.cdn-apple.com/2023SummerFCS/fullrestores/032-97896/E2423AEB-4517-4FEA-921C-662FDF1B784F/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_7.5_20P5060_Restore.ipsw
https://updates.cdn-apple.com/2023SpringFCS/fullrestores/032-42172/F41836DF-78E0-46A8-904E-5626FBD3BE12/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_7.5_20P5058_Restore.ipsw
https://updates.cdn-apple.com/2023WinterFCS/fullrestores/002-76054/688190D4-629D-489E-ABB2-73460584AA36/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_7.4_20P4252_Restore.ipsw
https://updates.cdn-apple.com/2020/macos/001-36803-20200810-A97B835C-DB65-11EA-B99D-EC2029ACBA60/iBridge2,1,iBridge2,10,iBridge2,12,iBridge2,14,iBridge2,15,iBridge2,16,iBridge2,19,iBridge2,20,iBridge2,21,iBridge2,22,iBridge2,3,iBridge2,4,iBridge2,5,iBridge2,6,iBridge2,7,iBridge2,8_4.6_17P6610_Restore.ipsw
http://appldnld.apple.com/macos/091-45512-20180123-AD6E4F3A-0075-11E8-88FB-57C37CCC33A9/iBridge2,1_2.0.1_15P2542_Restore.ipsw
https://updates.cdn-apple.com/2019FallFCS/fullrestores/091-99503/DCBD0A9C-D986-11E9-BB0A-9520DCDBD6A3/iPad_64bit_TouchID_13.1_17A844_Restore.ipsw
https://updates.cdn-apple.com/2020/patches/001-88117/BD41C2A1-A926-4656-8249-EA4094214EEB/com_apple_MobileAsset_MobileAccessoryUpdate_A1999-19G_EA/2406745b4affd224462f0a37a37b82edfb060a99.zip
https://updates.cdn-apple.com/2023WinterFCS/patches/694-69223/49A6DFAE-9681-498A-A2A5-04FC5A2A1E6A/com_apple_MobileAsset_DarwinAccessoryUpdate_A2525/787877d2eee7e2b879bece85e2c8b3a43273575c.zip
https://updates.cdn-apple.com/2024FallFCS/fullrestores/072-10659/6F6AC086-236B-4B67-B915-23E1F53A00D8/AppleTV5,3_18.1_22J580_Restore.ipsw
https://updates.cdn-apple.com/2020SummerFCS/fullrestores/041-32406/CEA5A7EB-2514-4EA3-B872-E3AB19716E11/AppleTV5,3_14.0_18J386_Restore.ipsw
https://updates.cdn-apple.com/2018FallFCS/fullrestores/091-62602/ECAE0C62-AC8C-11E8-BEAA-FD5745E6A746/AppleTV5,3_12.0_16J364_Restore.ipsw
https://updates.cdn-apple.com/2020SummerFCS/patches/041-32404/00A5C893-B5F3-4917-BFC1-FBC2034E090B/com_apple_MobileAsset_SoftwareUpdate/c8540b04f73285d6c5a3c08d0f893ecf6003688b.zip
https://appledb.dev/device/Apple-TV-4K-(3rd-generation)
https://updates.cdn-apple.com/2024SummerFCS/patches/062-52692/DEF198E2-6C5D-4BDA-ADC2-5461828D95F1/com_apple_MobileAsset_SoftwareUpdate/aae08244572800504efd04dbac2fa4b5f3ffb16e.zip
https://appledb.dev/device/identifier/AppleTV11,1
https://updates.cdn-apple.com/2024SummerFCS/patches/062-52686/97E06A54-7E56-4A41-A52C-5A821CC1B780/com_apple_MobileAsset_SoftwareUpdate/56acb5ada116d7fa90a39d89acfd79109d7dfa68.zip
https://appledb.dev/device/identifier/AppleTV6,2
https://updates.cdn-apple.com/2024SummerFCS/patches/062-52640/1EEE32F3-92F5-410B-AD72-25A8062FA896/com_apple_MobileAsset_SoftwareUpdate/689e4f129d9182443572da09507d273637428b90.zip
https://appledb.dev/device/identifier/AppleTV5,3
https://updates.cdn-apple.com/2024SummerFCS/fullrestores/062-52542/B6A7E948-76E4-4BD2-8A8C-77C80DADAB3C/AppleTV5,3_17.6.1_21M80_Restore.ipsw
https://updates.cdn-apple.com/2024FallFCS/patches/072-10761/B274A4AF-E5D4-4E06-A217-E6D50C18E32B/com_apple_MobileAsset_SoftwareUpdate/5ac2d7785ea93d18f97a38b533b39b23bcd85a23.zip
https://updates.cdn-apple.com/2024FallFCS/patches/072-10752/C233FFB9-D39A-4862-8D97-7AA7B0616185/com_apple_MobileAsset_SoftwareUpdate/746856b4bbb4441d3192c9503c0038a544354208.zip
http://appldnld.apple.com/tvos11.1/091-19198-20171030-05EF0814-B906-11E7-B84C-F7134A06F813/com_apple_MobileAsset_SoftwareUpdate/c5a35ea26e65932eab93fdb4d0d6545fb1d1fbea.zip
https://secure-appldnld.apple.com/tvos11.1/091-19200-20171030-6454C934-B906-11E7-8129-FF5DBDA7E146/AppleTV5,3_11.1_15J582_Restore.ipsw
https://updates.cdn-apple.com/2018/tvos/091-73040-20180709-39AF81A0-7C1B-11E8-BFD6-5557544C24EB/AppleTV5,3_11.4.1_15M73_Restore.ipsw
https://updates.cdn-apple.com/2018/tvos/091-65364-20180529-C5AEAD16-5AB5-11E8-A840-752442FD93D5/AppleTV5,3_11.4_15L577_Restore.ipsw
https://secure-appldnld.apple.com/tvos11.2.5/091-39274-20180122-53A42726-FAFE-11E7-AA64-27642C55F105/AppleTV5,3_11.2.5_15K552_Restore.ipsw
https://secure-appldnld.apple.com/tvos11/091-32536-20170912-5ACCEDF2-9641-11E7-BEDA-F982B54D2808/AppleTV5,3_11.0_15J381_Restore.ipsw
https://secure-appldnld.apple.com/tvos10.0/031-76856-20160916-B770B2D0-722C-11E6-8D32-1C4033D2D062/AppleTV5,3_10.0_14T330_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52538/C92610C4-12AF-4CB7-A4D3-3D2CB2CB50F6/iPad_64bit_TouchID_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52644/08FA8208-95F6-438D-BE19-111BBBCA6B79/com_apple_MobileAsset_SoftwareUpdate/0cfde5354872e726156236f6066b6576971188de.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52462/29123DD2-A5B2-4EFB-BDD2-614F6164D4C3/iPadPro_9.7_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52478/1FB662E2-BAFA-4D38-BFF5-17B1E13CC568/com_apple_MobileAsset_SoftwareUpdate/57a1a11984c6a6048e47f4cde1828d56600376d1.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52403/229C9F55-5340-4BB6-A908-046481D6DCFD/iPadPro_12.9_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52612/56E51B96-CCC0-4000-BE40-F609820BE5A3/com_apple_MobileAsset_SoftwareUpdate/460e5925000922d9e53c7ba98c339847195a2153.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52700/0773CE23-EC27-46CF-A8D5-35ECEED7C66C/iPad_64bit_TouchID_ASTC_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52765/A69F362D-D8B8-43C8-AECE-0E8AE52C0B0A/com_apple_MobileAsset_SoftwareUpdate/2571875093d1d2e0d674cdadc9f5823ed8373ea7.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52482/66122FCF-FCC4-409C-86B5-560DB2D222AF/iPad_Pro_HFR_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52418/2085C916-ADC0-4190-8084-FA59A7245BCD/com_apple_MobileAsset_SoftwareUpdate/2c34ae47de7ff56cb680335d054795b8f1904b95.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52589/64AF33C6-D2F7-4C28-ABA4-F81BA16B2C29/iPad_10.2_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52680/6F54FF55-948B-4001-B3C1-DD6ED2CB5B6E/com_apple_MobileAsset_SoftwareUpdate/6d202407437049ecd23712f48f32691b0c67680e.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52697/111D8138-7A8E-46D0-96B5-BA435F1D2EC0/iPad_Pro_A12X_A12Z_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52728/1E26AEFA-0854-4C01-8D0D-079E533B4EF0/com_apple_MobileAsset_SoftwareUpdate/b285cb456b13963c3c3f42deb56793ce74367961.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52625/EEA0A036-DF3B-4A2B-A878-D8A897AFCA95/iPad_Spring_2019_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52726/C5BE38C1-91DD-43F9-A481-B7E3272C81FF/com_apple_MobileAsset_SoftwareUpdate/f5a29ddc1bb4fc5b7b73e3f9208796ae7d300a13.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52484/40DEEBC7-FA0C-4FA9-B851-A4B7D071B44F/iPad_10.2_2020_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52603/21BA12EB-9178-4015-BB45-58D56FCD7604/com_apple_MobileAsset_SoftwareUpdate/3e9eff290650e5238f4936e726c508a64208ca8f.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52489/E2F9C101-644A-4FC4-AD8B-57FECF44B656/iPad_10.2_2021_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52757/10F88B29-B107-4DD6-97CB-09670CE4DC73/com_apple_MobileAsset_SoftwareUpdate/ffde477867f8acd4b117dfb619630482812e8f88.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52725/7820A74E-06CF-455F-A3D8-F2D6DE5017B4/iPad_Fall_2020_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52798/24CB8B7F-4D04-42C0-8F77-D707AD556998/com_apple_MobileAsset_SoftwareUpdate/f237f02f112f40af672511641c4fac472283c44a.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52558/6D1507A5-8211-4D43-9B32-D1207E2684B3/iPad_Pro_Spring_2021_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52676/B741EF85-3764-4A7C-8A10-3095E9E6D69F/com_apple_MobileAsset_SoftwareUpdate/f6ebb21cb4002ebb3b397acae589d4a7d01fd271.zip
https://updates.cdn-apple.com/2022WinterSeed/fullrestores/002-52581/EB32C9EC-21A5-453B-AF19-9C08E85D5C2E/iPad_Fall_2021_15.3_19D5040e_Restore.ipsw
https://updates.cdn-apple.com/2022WinterSeed/patches/002-52377/A578F0E8-E401-473A-A70E-76F3D93DEA59/com_apple_MobileAsset_SoftwareUpdate/2a8a3853daa80f87fc9fedb5980d581f025ad64d.zip
https://updates.cdn-apple.com/2021SummerSeed/fullrestores/071-55310/E5EAD251-C5F4-46FB-B5E7-62AC0B3F3EF3/AppleTV5,3_15.0_19J5288e_Restore.ipsw
https://updates.cdn-apple.com/2021FallSeed/fullrestores/002-17637/C02D3161-60D3-4612-940E-36F9B2E40E0E/AppleTV5,3_15.1_19J5567a_Restore.ipsw
https://updates.cdn-apple.com/2021FallSeed/patches/002-17641/F2E587E9-A766-40ED-B8FB-1E6E07E32490/com_apple_MobileAsset_SoftwareUpdate/f6d232467223d384bf74229fbc5bbd8666c102b2.zip
https://updates.cdn-apple.com/2021FallSeed/patches/002-17647/C2485FA3-7132-45D7-8DE7-439AB1AFECDE/com_apple_MobileAsset_SoftwareUpdate/6b3d849f2d4465c2fe3bf14853aacf309ec3a72c.zip
https://updates.cdn-apple.com/2021FallSeed/patches/002-17663/E98A3380-B161-4ACA-9584-879043F47DB6/com_apple_MobileAsset_SoftwareUpdate/59b82e3d219c041af6fe79cbeddf45403496e05e.zip
""".strip().splitlines()

# urls = """
# https://appledb.dev/device/identifier/iPod7,1
# https://secure-appldnld.apple.com/ios9/058-11554-20150916-2D012EAC-5678-11E5-B1A1-F5F76CA99CB1/iPod7,1_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/identifier/iPod5,1
# https://secure-appldnld.apple.com/ios9/058-21788-20150916-01FB67DA-5679-11E5-897E-8AF96CA99CB1/iPod5,1_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPhone-6-series
# http://appldnld.apple.com/ios9/058-11566-20150916-E5FE2B8A-5678-11E5-ABA0-42F96CA99CB1/iPhone7,1_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/031-29698-20150916-ECC56014-5678-11E5-9EA3-66F96CA99CB1/iPhone7,2_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPhone-5s
# http://appldnld.apple.com/ios9/058-25026-20150916-2D01E630-5678-11E5-88C3-FEF76CA99CB1/iPhone6,1_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/058-21808-20150916-2D0C9B84-5678-11E5-A514-FFF76CA99CB1/iPhone6,2_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPhone-5c
# https://secure-appldnld.apple.com/ios9/058-12416-20150916-2D014842-5678-11E5-8BA0-FBF76CA99CB1/iPhone5,3_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/031-28090-20150916-2D01D21C-5678-11E5-B696-FCF76CA99CB1/iPhone5,4_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPhone-5
# https://secure-appldnld.apple.com/ios9/058-21825-20150916-2CFEADD0-5678-11E5-9EC1-F7F76CA99CB1/iPhone5,1_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/058-23601-20150916-2D01837A-5678-11E5-97A2-F9F76CA99CB1/iPhone5,2_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/identifier/iPhone4,1
# https://secure-appldnld.apple.com/ios9/058-25016-20150916-131EC4B2-5679-11E5-BBE9-BCF96CA99CB1/iPhone4,1_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-mini-3
# http://appldnld.apple.com/ios9/058-23478-20150916-2CFF47FE-5678-11E5-9A20-EBF76CA99CB1/iPad4,9_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/058-21830-20150916-2CFF2E9A-5678-11E5-8021-E7F76CA99CB1/iPad4,8_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/058-22776-20150916-2CFC8B36-5678-11E5-BFB0-E3F76CA99CB1/iPad4,7_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-mini-2
# http://appldnld.apple.com/ios9/031-28094-20150916-2CFDD040-5678-11E5-B196-E5F76CA99CB1/iPad4,5_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/058-18871-20150916-2CFD931E-5678-11E5-8C06-E2F76CA99CB1/iPad4,4_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/058-12414-20150916-2CFDCA96-5678-11E5-BB80-E9F76CA99CB1/iPad4,6_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-mini
# https://secure-appldnld.apple.com/ios9/058-18877-20150916-5C3330C0-5679-11E5-A105-4AFB6CA99CB1/iPad2,7_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/031-29704-20150916-5303B98E-5679-11E5-B532-D4FA6CA99CB1/iPad2,6_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/058-26588-20150916-3C31FB08-5679-11E5-AB3F-6CFA6CA99CB1/iPad2,5_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-Air-2
# http://appldnld.apple.com/ios9/031-24750-20150916-2CFBC9DA-5678-11E5-B600-DFF76CA99CB1/iPad5,4_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/058-11516-20150916-2CFC6282-5678-11E5-BA4A-DDF76CA99CB1/iPad5,3_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-Air
# http://appldnld.apple.com/ios9/058-18870-20150916-2CFAE772-5678-11E5-A803-D9F76CA99CB1/iPad4,2_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/031-29716-20150916-2CFBDC18-5678-11E5-ADBD-D7F76CA99CB1/iPad4,1_9.0_13A344_Restore.ipsw
# http://appldnld.apple.com/ios9/031-29700-20150916-2CFAB66C-5678-11E5-BBD7-DBF76CA99CB1/iPad4,3_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-(4th-generation)
# https://secure-appldnld.apple.com/ios9/058-11538-20150916-31C2C42C-5679-11E5-A8ED-53FA6CA99CB1/iPad3,6_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/058-11511-20150916-1E17FD20-5679-11E5-8E15-03FA6CA99CB1/iPad3,5_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/031-24741-20150916-18D8E4DC-5679-11E5-8CA2-E1F96CA99CB1/iPad3,4_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-(3rd-generation)
# https://secure-appldnld.apple.com/ios9/058-23607-20150916-2CFB4D66-5678-11E5-BF79-D3F76CA99CB1/iPad3,2_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/058-18866-20150916-2CFAD7A0-5678-11E5-942F-D5F76CA99CB1/iPad3,3_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/031-25660-20150916-2CFAB8F6-5678-11E5-80CC-D1F76CA99CB1/iPad3,1_9.0_13A344_Restore.ipsw
# https://appledb.dev/device/iPad-2
# https://secure-appldnld.apple.com/ios9/058-25009-20150916-2D002BEC-5678-11E5-9B61-F1F76CA99CB1/iPad2,2_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/058-11514-20150916-2CFEFA92-5678-11E5-BF5C-F4F76CA99CB1/iPad2,3_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/058-15433-20150916-2CFDDE78-5678-11E5-B33D-EDF76CA99CB1/iPad2,1_9.0_13A344_Restore.ipsw
# https://secure-appldnld.apple.com/ios9/058-21841-20150916-2CFDAEDA-5678-11E5-A181-EFF76CA99CB1/iPad2,4_9.0_13A344_Restore.ipsw
# """.strip().splitlines()

# urls = """
# https://secure-appldnld.apple.com/tvos11.3/091-45726-201803029-8EA84462-2B9E-11E8-936C-EE5C04115E15/AppleTV5,3_11.3_15L211_Restore.ipsw
# https://secure-appldnld.apple.com/tvos11.2.6/091-70058-20180220-9EE97426-1335-11E8-BC69-D0A6E0A71A1F/AppleTV5,3_11.2.6_15K600_Restore.ipsw
# https://secure-appldnld.apple.com/tvos11.2.5/091-39274-20180122-53A42726-FAFE-11E7-AA64-27642C55F105/AppleTV5,3_11.2.5_15K552_Restore.ipsw
# https://secure-appldnld.apple.com/tvos11.2.1/091-55968-20171213-A1B14924-DDF0-11E7-8351-65D73E58CDD2/AppleTV5,3_11.2.1_15K152_Restore.ipsw
# https://secure-appldnld.apple.com/tvos11.2/091-51265-20171204-CE2A0AB0-D4CA-11E7-A3A2-76502EDC3D3E/AppleTV5,3_11.2_15K106_Restore.ipsw
# https://secure-appldnld.apple.com/tvos11.1/091-19200-20171030-6454C934-B906-11E7-8129-FF5DBDA7E146/AppleTV5,3_11.1_15J582_Restore.ipsw
# https://secure-appldnld.apple.com/tvos11/091-32536-20170912-5ACCEDF2-9641-11E7-BEDA-F982B54D2808/AppleTV5,3_11.0_15J381_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.2.2/091-23452-20170720-5D53229C-6A56-11E7-8577-8B2C4A4DD6D5/AppleTV5,3_10.2.2_14W756_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.2.1/031-93360-20170515-3502FD70-3442-11E7-B3DB-E56B2DBC0DB3/AppleTV5,3_10.2.1_14W585a_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.2/031-52186-20170320-71EFBAE0-0B37-11E7-804A-A4A7FF9FED6C/AppleTV5,3_10.2_14W265_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.1.1/031-86873-20170117-B837ADDC-D950-11E6-B0D8-F31FD55B5B9D/AppleTV5,3_10.1.1_14U712a_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.1/031-69370-20161205-23778294-B8C1-11E6-95A5-C74CE47229E1/AppleTV5,3_10.1_14U593_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.0.1/031-91431-20161109-3F9F616A-A770-11E6-BD96-A8C6F9858D7F/AppleTV5,3_10.0.1_14U100_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.0.1/031-59447-20161024-AA217A0A-9483-11E6-A69F-635E80A31755/AppleTV5,3_10.0.1_14U71_Restore.ipsw
# https://secure-appldnld.apple.com/tvos10.0/031-76856-20160916-B770B2D0-722C-11E6-8D32-1C4033D2D062/AppleTV5,3_10.0_14T330_Restore.ipsw
# https://secure-appldnld.apple.com/tvOS9.2.2/031-59012-20160718-EF9FAF26-42FC-11E6-BF52-BED4C1708330/AppleTV5,3_9.2.2_13Y825_Restore.ipsw
# https://secure-appldnld.apple.com/tvos9.2.1/031-46327-20160516-FFB07AF6-13CE-11E6-AE7B-93E0400DF7EB/AppleTV5,3_9.2.1_13Y772_Restore.ipsw
# https://secure-appldnld.apple.com/tvOS9.2/031-35933-20160321-7C5F40E6-E7B5-11E5-92FF-5A5CBD379832/AppleTV5,3_9.2_13Y234_Restore.ipsw
# https://secure-appldnld.apple.com/tvos9.1.1/031-49466-20160125-A31FCFA8-C068-11E5-97DF-0E0A1F993B90/AppleTV5,3_9.1.1_13U717_Restore.ipsw
# https://secure-appldnld.apple.com/tvos9.1/031-32682-20151208-2B49C4A0-9ABD-11E5-8CE9-A56EF5563FD9/AppleTV5,3_9.1_13U85_Restore.ipsw
# https://secure-appldnld.apple.com/tvos9.0.1/031-42666-20151109-9980F56E-8367-11E5-986E-6F228B8BECEB/AppleTV5,3_9.0.1_13T402_Restore.ipsw
# https://secure-appldnld.apple.com/tvos9.0/031-24288-20151028-1BE4479A-7DDC-11E5-BDEE-974E5942017F/AppleTV5,3_9.0_13T396_Restore.ipsw
# """.strip().splitlines()

# urls = """
# https://updates.cdn-apple.com/2024/patches/052-48536/331B264D-14D9-4346-81F6-F15D94DA7E15/com_apple_MobileAsset_UARP_A2580/55b6f0d5567783d9fd9071105ae3e0e88a8303eb.zip
# https://appledb.dev/device/AirPods-Pro-(2nd-generation,-USB-C)
# https://updates.cdn-apple.com/2024/patches/062-96968/42FF7B8A-35F0-4250-8D11-7BAC91012AAD/com_apple_MobileAsset_UARP_A2968/b94c2ff940d74185130bd58b4165bbb3fa3f8a94.zip
# https://updates.cdn-apple.com/2024/patches/062-96967/ADB3A8B7-0F49-4075-A7B1-D5BBBA7658FC/com_apple_MobileAsset_UARP_A3048/03db24e6497173170ff4a6bbf465ffda0352c07b.zip
# https://appledb.dev/device/Beats-Fit-Pro-series
# https://updates.cdn-apple.com/2024/patches/042-95146/E33093AD-2E8F-415A-995D-92719BE3794A/com_apple_MobileAsset_MobileAccessoryUpdate_A2577_EA/5a3758123d5ba1039af32271f159bdaf3cb3fd38.zip
# https://appledb.dev/device/Powerbeats-Pro-(2020)-series
# https://updates.cdn-apple.com/2024/patches/042-95144/80FEC818-685F-4D16-AEE8-78ADDA359B4B/com_apple_MobileAsset_MobileAccessoryUpdate_A2048_EA/558ab4a07f8d1207cd3564f345c4da938235e453.zip
# https://appledb.dev/device/Powerbeats-Pro-(2019)
# https://updates.cdn-apple.com/2024/patches/062-08773/064A7EC6-DE5A-4D0C-8DCD-587885D2B59C/com_apple_MobileAsset_UARP_A2968/3b6023eac227bdbb629925379522f2f3563456e0.zip
# https://updates.cdn-apple.com/2024/patches/062-08772/71286AFD-F562-4A3D-885D-7287BD771662/com_apple_MobileAsset_UARP_A3048/81f728f5cb818f297e6656072022b69aaf591c0f.zip
# https://appledb.dev/device/AirPods-Pro-(2nd-generation)
# https://updates.cdn-apple.com/2024/patches/062-08774/47972354-2E45-4538-BDE4-E4FFE2283F15/com_apple_MobileAsset_UARP_A2618/e44812c0063bd44740849ce35e910c8425490678.zip
# https://appledb.dev/device/AirPods-(3rd-generation)
# https://updates.cdn-apple.com/2024/patches/052-35617/09DDC509-81AF-4D67-906A-0700A05C5F79/com_apple_MobileAsset_MobileAccessoryUpdate_A2564_EA/234b837c77f964eb1544885b922490af2d6fb581.zip
# https://appledb.dev/device/identifier/iProd8,6
# https://updates.cdn-apple.com/2024/patches/062-09878/4FCC6354-D029-403E-9121-3C43719BE2A2/com_apple_MobileAsset_MobileAccessoryUpdate_A2096_EA/27d49f4660f176bfb7c1790e811b24eaee8147d2.zip
# https://appledb.dev/device/AirPods-Pro-(1st-generation)
# https://updates.cdn-apple.com/2024/patches/052-35616/2BC5B834-B942-450D-970B-CE184E1CDC63/com_apple_MobileAsset_MobileAccessoryUpdate_A2084_EA/efac7cade5ff07a2385dce18ff8e2fc0d3ca2e20.zip
# https://appledb.dev/device/AirPods-(2nd-generation)
# https://updates.cdn-apple.com/2024/patches/052-35615/43870D85-C518-4636-84B1-39994ADBE22E/com_apple_MobileAsset_MobileAccessoryUpdate_A2032_EA/d5eeeaa57de1d6803b2df30ab5192b853f6a11d4.zip
# https://updates.cdn-apple.com/2024/patches/052-26971/4F8823C0-21C9-4AF0-8C35-F234B97C1D3E/com_apple_MobileAsset_MobileAccessoryUpdate_A2564_EA/677456b8ad49925c360befd194264c8bdcefe060.zip
# https://updates.cdn-apple.com/2022/patches/012-38032/084F0D70-E80B-4B73-B1DF-61BD19AE602C/com_apple_MobileAsset_MobileAccessoryUpdate_A2577_EA/79c118138e6f5f03be21a101a316e3bf6923be43.zip
# https://updates.cdn-apple.com/2022/patches/012-38043/8C1DF89B-595A-4150-AF82-9D0CFD8542BE/com_apple_MobileAsset_MobileAccessoryUpdate_A2048_EA/767cf4a1ccb9ec07e9e7e783178b8483d7a5a728.zip
# https://appledb.dev/device/Beats-Solo-Pro
# https://updates.cdn-apple.com/2021/patches/061-83287/DD36BB1F-85DA-47EE-992A-93EAFE671888/com_apple_MobileAsset_MobileAccessoryUpdate_A1881_EA/70e8610badb0d9b53ce5849c7a92d33503579e98.zip
# https://updates.cdn-apple.com/2021/patches/071-70915/49BA63A2-D2C7-4FF3-86B2-3DF8F4D056CA/com_apple_MobileAsset_MobileAccessoryUpdate_A2048_EA/7c07d4e0de7cfbac80893e31be8d0f85c8d5350c.zip
# https://appledb.dev/device/Powerbeats-(4th-generation)
# https://updates.cdn-apple.com/2021/patches/061-83285/A42BB3FE-51ED-4F3C-B4FB-9FFF9FF12BC8/com_apple_MobileAsset_MobileAccessoryUpdate_A2015_EA/28061cf02361df358d3b4caadbe37c8c7a9c8be1.zip
# https://updates.cdn-apple.com/2024/patches/072-08222/7D3818CA-667A-4CB0-892D-8067E53994A9/com_apple_MobileAsset_MobileAccessoryUpdate_A2564_EA/a7fca2b0f36a54a15ae9500afff9fd2401ee9a2c.zip
# https://updates.cdn-apple.com/2024/patches/072-08223/4DB8BACA-0057-47CE-86BF-36B31472B83E/com_apple_MobileAsset_MobileAccessoryUpdate_A2096_EA/a363be8ae46246f5f86ca15fecc64961c200687f.zip
# https://updates.cdn-apple.com/2024/patches/072-08224/12321BD3-668A-47A7-A18D-D19702E75879/com_apple_MobileAsset_MobileAccessoryUpdate_A2084_EA/6b1b5d61616c37e877f016499253424bff4b018d.zip
# https://updates.cdn-apple.com/2024/patches/072-08221/12EDB45C-44EF-47FA-BD8D-8711E7189923/com_apple_MobileAsset_MobileAccessoryUpdate_A2032_EA/5159cb69f972e6ca74802b5bd8c4460e13eb3e79.zip
# https://updates.cdn-apple.com/2020/patches/001-59560/C6A5454F-FEF0-4451-A44B-6538D1D1AFA2/com_apple_MobileAsset_MobileAccessoryUpdate_A2096_EA/4f8f1d6c10bdc9406187aecaa14251539730c169.zip
# https://updates.cdn-apple.com/2020/patches/041-94891/9911B253-600A-4F4D-92A8-5D55452C5BCE/com_apple_MobileAsset_MobileAccessoryUpdate_A1881_EA/64396db253b960e7024cc6832da4ac05aa7ff658.zip
# https://updates.cdn-apple.com/2020/patches/061-97494/D564BE71-4613-489A-B68B-DA8614AE252A/com_apple_MobileAsset_MobileAccessoryUpdate_A2048_EA/68d6d859207542febe207c2ee9bb70b561fd5dcc.zip
# https://updates.cdn-apple.com/2020/patches/001-43440/BCEB69A8-1074-48E1-8FB9-6102AC4FE937/com_apple_MobileAsset_MobileAccessoryUpdate_A2084_EA/cc9847d7a89fffc28dc0eaae8178969cc05ea2b1.zip
# https://updates.cdn-apple.com/2020/patches/061-97496/A9A52576-ACA6-4783-9C61-5778C41704C9/com_apple_MobileAsset_MobileAccessoryUpdate_A2032_EA/f6dad1df30812ee08eb0d7bccbef92d92cfe9d45.zip
# https://updates.cdn-apple.com/2024/patches/052-68706/E2D82D32-2895-4FE8-9432-5AEDCC5E6C2B/com_apple_MobileAsset_MobileAccessoryUpdate_DurianFirmware/e91ce06eb72cba76629c546f635ae2cb777407e5.zip
# https://updates.cdn-apple.com/2021/patches/071-45785/4132D4FE-1C5A-498E-8A6D-678A026679AF/com_apple_MobileAsset_MobileAccessoryUpdate_DurianFirmware/ae34f4b8aec8a4d4562227109be101728b7bef20.zip
# https://updates.cdn-apple.com/2022FCSWinter/patches/694-34933/73C7763D-6DB5-42D9-8B84-F22DCAF6ECB6/com_apple_MobileAsset_DarwinAccessoryUpdate_A2525/48013376924d2561a862d49a48085a02f6359496.zip
# https://updates.cdn-apple.com/2023FallFCS/patches/694-78114/2014C85F-15D6-4272-9C06-162A0097BB72/com_apple_MobileAsset_DarwinAccessoryUpdate_A2525/701917b0dbe43ac1a627fd509b32a322cd30b09e.zip
# https://updates.cdn-apple.com/2022SpringSeed/patches/694-47134/54E7312A-31E3-4B69-824A-84BBFE3C9A5C/com_apple_MobileAsset_DarwinAccessoryUpdate_A2525/585ef93cccf1120248c922b45eda0a7a28dae10b.zip
# """.strip().splitlines()

# https://secure-appldnld.apple.com/tvos10.0/031-76856-20160916-B770B2D0-722C-11E6-8D32-1C4033D2D062/AppleTV5,3_10.0_14T330_Restore.ipsw


# urls = """
# https://updates.cdn-apple.com/2024FallFCS/fullrestores/062-24440/7BFC888F-2CDA-4E5A-A4DC-D51DE28D3E7F/iPad16,1,iPad16,2_18.1_22B82_Restore.ipsw
# """.strip().splitlines()

# urls = """
# https://updates.cdn-apple.com/private-cloud-compute/785bfb42fe05a972d46b774936e53c5cdfa79149ed7ac5dee6a27262f9c6512c
# https://updates.cdn-apple.com/private-cloud-compute/a1245d6d56b3de6009d1bbfe452262ff2e953034636e9b47d83e4c2a2d2540f7
# """.strip().splitlines()

# urls = """
# https://updates.cdn-apple.com/2024FallFCS/patches/072-12298/C6D21056-F426-45FA-8E5E-AE4C7BFF3B9F/com_apple_MobileAsset_MacSoftwareUpdate/fdea015ea92c9cc73c66f5fd4a3555e4aca85340.zip
# """.strip().splitlines()

urls = """
https://updates.cdn-apple.com/2024FallFCS/fullrestores/072-41951/5790575D-5E1C-472E-8CC2-86E297A25AFD/UniversalMac_15.2_24C2101_Restore.ipsw
""".strip().splitlines()

urls = """
https://updates.cdn-apple.com/2025WinterFCS/fullrestores/072-35515/856AC7E0-C306-4F4D-9430-962B6BBB4A95/iPhone17,5_18.3.1_22D8075_Restore.ipsw
""".strip().splitlines()

urls = """
https://updates.cdn-apple.com/2024FallFCS/fullrestores/072-41951/5790575D-5E1C-472E-8CC2-86E297A25AFD/UniversalMac_15.2_24C2101_Restore.ipsw
https://updates.cdn-apple.com/2025WinterFCS/fullrestores/072-35515/856AC7E0-C306-4F4D-9430-962B6BBB4A95/iPhone17,5_18.3.1_22D8075_Restore.ipsw
https://updates.cdn-apple.com/2021FallSeed/fullrestores/002-17637/C02D3161-60D3-4612-940E-36F9B2E40E0E/AppleTV5,3_15.1_19J5567a_Restore.ipsw
https://secure-appldnld.apple.com/tvos10.0/031-76856-20160916-B770B2D0-722C-11E6-8D32-1C4033D2D062/AppleTV5,3_10.0_14T330_Restore.ipsw
https://appledb.dev/device/iPhone-16-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91871/497C564A-C218-4F10-A972-259825D2E04C/iPhone17,2_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91923/41065B07-3F6C-4739-A8FD-AD3B637B7ACA/iPhone17,1_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-16-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91807/9143E33C-8702-4FBE-BFCE-58BA78745783/iPhone17,4_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91954/59B1415B-7F91-4CB6-952D-F688F7F73C24/iPhone17,3_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-15-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91823/78513D79-8C97-4D82-9016-96A7B0B40F89/iPhone16,2_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91945/73C7A123-6CBE-4E68-B34C-D6BD5017C518/iPhone16,1_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-15-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91993/C78E2855-4669-4C5B-9688-01798397232F/iPhone15,5_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92148/462D18EC-2A2A-447F-B881-269F9FCA6526/iPhone15,4_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-14-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92088/F6CA339F-D965-47AF-8D45-3FDFF6C3241E/iPhone15,3_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92069/31517E26-5A71-4126-ADD8-86448DF37409/iPhone15,2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone14,6
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91908/3EE63E9D-95DA-4F03-BC52-2B91A5B47A45/iPhone14,6_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone12,8
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92028/D64154C3-72AD-414A-8697-DD6E651BCA11/iPhone12,8_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone11,8
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91893/FE047A06-678C-4B5E-9673-829F17BD4DB0/iPhone11,8_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-14-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91864/F471F689-D43A-49FB-AD70-02BAB1F813DD/iPhone14,8_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91912/A4942C4D-53AE-4F9D-9C4F-10E70DB299E6/iPhone14,7_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-13-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92146/99E58869-F1FE-45E0-B16B-5FEEC384E576/iPhone14,3_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92002/160B4FD6-1FED-4B51-84BC-669D49F78631/iPhone14,2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-13-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92096/8CC4B9F0-5B81-47A8-8F61-9EAE6F3017BF/iPhone14,4_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92055/D6D4A1BB-8A19-434C-8998-008CDC4870BD/iPhone14,5_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-12-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91968/268D34D7-AF6A-40D8-94FA-AA5E81E4FB99/iPhone13,2,iPhone13,3_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92065/FB5B6C88-677B-4B27-B2A1-2063F5A406A8/iPhone13,4_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-12-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92040/B8E580AF-D63B-4D27-BDE1-7062B57AD35F/iPhone13,1_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91968/268D34D7-AF6A-40D8-94FA-AA5E81E4FB99/iPhone13,2,iPhone13,3_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-11-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91788/E63FFD63-0693-4B3D-A24D-AB25B5A8E662/iPhone12,3,iPhone12,5_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone12,1
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91944/D6495674-D7AD-46FD-A8E3-BBB9B23C2A16/iPhone12,1_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-XS-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91779/AC120C63-3A67-4D1E-B99F-6BE4ECA1C482/iPhone11,2,iPhone11,4,iPhone11,6_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-16-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91871/497C564A-C218-4F10-A972-259825D2E04C/iPhone17,2_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91923/41065B07-3F6C-4739-A8FD-AD3B637B7ACA/iPhone17,1_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-16-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91807/9143E33C-8702-4FBE-BFCE-58BA78745783/iPhone17,4_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91954/59B1415B-7F91-4CB6-952D-F688F7F73C24/iPhone17,3_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-15-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91823/78513D79-8C97-4D82-9016-96A7B0B40F89/iPhone16,2_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91945/73C7A123-6CBE-4E68-B34C-D6BD5017C518/iPhone16,1_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-15-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91993/C78E2855-4669-4C5B-9688-01798397232F/iPhone15,5_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92148/462D18EC-2A2A-447F-B881-269F9FCA6526/iPhone15,4_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-14-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92088/F6CA339F-D965-47AF-8D45-3FDFF6C3241E/iPhone15,3_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92069/31517E26-5A71-4126-ADD8-86448DF37409/iPhone15,2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone14,6
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91908/3EE63E9D-95DA-4F03-BC52-2B91A5B47A45/iPhone14,6_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone12,8
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92028/D64154C3-72AD-414A-8697-DD6E651BCA11/iPhone12,8_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone11,8
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91893/FE047A06-678C-4B5E-9673-829F17BD4DB0/iPhone11,8_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-14-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91864/F471F689-D43A-49FB-AD70-02BAB1F813DD/iPhone14,8_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91912/A4942C4D-53AE-4F9D-9C4F-10E70DB299E6/iPhone14,7_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-13-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92146/99E58869-F1FE-45E0-B16B-5FEEC384E576/iPhone14,3_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92002/160B4FD6-1FED-4B51-84BC-669D49F78631/iPhone14,2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-13-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92096/8CC4B9F0-5B81-47A8-8F61-9EAE6F3017BF/iPhone14,4_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92055/D6D4A1BB-8A19-434C-8998-008CDC4870BD/iPhone14,5_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-12-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91968/268D34D7-AF6A-40D8-94FA-AA5E81E4FB99/iPhone13,2,iPhone13,3_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92065/FB5B6C88-677B-4B27-B2A1-2063F5A406A8/iPhone13,4_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-12-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92040/B8E580AF-D63B-4D27-BDE1-7062B57AD35F/iPhone13,1_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91968/268D34D7-AF6A-40D8-94FA-AA5E81E4FB99/iPhone13,2,iPhone13,3_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-11-Pro-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91788/E63FFD63-0693-4B3D-A24D-AB25B5A8E662/iPhone12,3,iPhone12,5_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/identifier/iPhone12,1
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91944/D6495674-D7AD-46FD-A8E3-BBB9B23C2A16/iPhone12,1_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPhone-XS-series
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91779/AC120C63-3A67-4D1E-B99F-6BE4ECA1C482/iPhone11,2,iPhone11,4,iPhone11,6_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-40072/0E423C7A-746E-4A3A-A58B-6F5248F2FA31/AppleTV5,3_18.4_22L5218l_Restore.ipsw
https://appledb.dev/device/iPad-mini-(A17-Pro)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91869/5EB317C8-2ED3-4EBA-8BEB-A2749C2955DE/iPad16,1,iPad16,2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-mini-(6th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92047/0D1C06DF-BECC-4DF5-AA0B-5B74032CD828/iPad_Fall_2021_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-mini-(5th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92132/5D02256F-4EEC-4988-AFEE-1244F7388D18/iPad_Spring_2019_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-13-inch-(M4)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91792/71351700-4785-4F5C-9656-447D2E18E2BC/iPad_Pro_M4_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-11-inch-(M4)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91792/71351700-4785-4F5C-9656-447D2E18E2BC/iPad_Pro_M4_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-12.9-inch-(6th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92177/201D8D40-1206-496C-AF32-7D62EC4B1B1A/iPad14,3,iPad14,4,iPad14,5,iPad14,6_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-11-inch-(4th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92177/201D8D40-1206-496C-AF32-7D62EC4B1B1A/iPad14,3,iPad14,4,iPad14,5,iPad14,6_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-12.9-inch-(5th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91863/203E34CA-2093-4333-ACB2-4F4C6DAEBEE6/iPad_Pro_Spring_2021_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-11-inch-(3rd-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91863/203E34CA-2093-4333-ACB2-4F4C6DAEBEE6/iPad_Pro_Spring_2021_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-12.9-inch-(4th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91916/7D0E0E1A-7F0A-42AD-894B-0978214F7BD2/iPad_Pro_A12X_A12Z_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-11-inch-(2nd-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91916/7D0E0E1A-7F0A-42AD-894B-0978214F7BD2/iPad_Pro_A12X_A12Z_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-12.9-inch-(3rd-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91916/7D0E0E1A-7F0A-42AD-894B-0978214F7BD2/iPad_Pro_A12X_A12Z_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Pro-11-inch-(1st-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91916/7D0E0E1A-7F0A-42AD-894B-0978214F7BD2/iPad_Pro_A12X_A12Z_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Air-13-inch-(M2)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91834/0EB32E63-18F8-428D-9BA7-048A601469BF/iPad_Air_M2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Air-11-inch-(M2)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91834/0EB32E63-18F8-428D-9BA7-048A601469BF/iPad_Air_M2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Air-(5th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92029/A015AB88-5AF8-4764-A136-4525EE95637D/iPad_Spring_2022_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Air-(4th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91985/15ED2B73-BA4E-4897-9911-4133BE7E0398/iPad_Fall_2020_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-Air-(3rd-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92132/5D02256F-4EEC-4988-AFEE-1244F7388D18/iPad_Spring_2019_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-(9th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91914/567CB829-01CB-4F24-819F-FA31A029F192/iPad_10.2_2021_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-(8th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-92085/CAC20774-579D-4B42-B745-C8C35A8964FF/iPad_10.2_2020_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-(7th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91839/A956E2B3-3F7F-4F4F-AF88-BB84A456348B/iPad_10.2_18.4_22E5200s_Restore.ipsw
https://appledb.dev/device/iPad-(10th-generation)
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-91931/40D8E706-5BE6-49E7-9DBE-86FA79D50EA0/iPad_Fall_2022_18.4_22E5200s_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-90551/F5479625-0E4A-403D-BF39-4420580E2260/Apple_Vision_Pro_2.4_22O5199o_Restore.ipsw

""".strip().splitlines()

urls = """
https://updates.cdn-apple.com/2025WinterSeed/patches/072-96957/CF9D42E4-12FE-457D-8154-60570AA75F4A/com_apple_MobileAsset_MacSoftwareUpdate/3e912194c8055a76afa006aef40b2a2e5a70f64b.zip
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-96972/D76A7AE6-3A35-4295-B102-E5FC5C84B4DC/UniversalMac_15.4_24E5228e_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/fullrestores/072-94493/8E7F8457-22B2-46C1-99A5-D21BC30CE347/iPhone17,5_18.4_22E5222f_Restore.ipsw
https://updates.cdn-apple.com/2025WinterSeed/patches/072-97944/6A987C2D-130C-419F-A050-5B949D21EF4B/com_apple_MobileAsset_MacSoftwareUpdate/f5e9e7881f8e7291d49406d8ecab04ae7624b898.zip
""".strip().splitlines()

urls = """
https://appledb.dev/device/identifier/iPhone18,4
https://updates.cdn-apple.com/2025FallFCS/mobileassets/062-16089/9D9BED55-A439-42D9-9669-CC56E6D019AD/com_apple_MobileAsset_SoftwareUpdate/d70b52b4965a877b5f65bef1dec78588f1984ca7e45610c76e8e85a27db08b9d.aea
https://appledb.dev/device/iPhone-17-Pro-series
https://updates.cdn-apple.com/2025FallFCS/mobileassets/062-16090/49E84A1A-9BD1-45BD-B932-0057E0A34A2E/com_apple_MobileAsset_SoftwareUpdate/d40bb52ce953a2a61cb39f726d35a086f63427a97ab7ea6a403fdfee9694381d.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/052-86537/7528C826-E4EC-4F5C-8775-95ACF1977E31/com_apple_MobileAsset_SoftwareUpdate/f56417cf63b4d372820894af000ec8d3f2939c24843b28fd8ddaea96730c0754.aea
https://appledb.dev/device/identifier/iPhone18,3
https://updates.cdn-apple.com/2025FallFCS/mobileassets/062-16077/9826928A-AA52-4ED6-9199-1C0D85700088/com_apple_MobileAsset_SoftwareUpdate/2afc05be1230e9807380573fd2d1a83245e3b6e02b8c9e17bb2e8a2d0961d534.aea
https://appledb.dev/device/identifier/iPhone17,5
https://updates.cdn-apple.com/2025FallFCS/fullrestores/052-69619/720ABE76-7655-4B63-851E-171BE30EA89B/iPhone17,5_26.0_23A340_Restore.ipsw
https://appledb.dev/device/Apple-Watch-Series-11
https://updates.cdn-apple.com/2025FallFCS/mobileassets/062-06889/90268AD0-E72D-43C4-89DC-E43953660F0B/com_apple_MobileAsset_SoftwareUpdate/7c1ff2c4eded6c70443f2aa5e682f2aedda9d901ca90c1872b4f87174cf81f3d.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/062-06886/C6F7775B-08BF-49EB-B9F2-6A41DD4F4FAC/com_apple_MobileAsset_SoftwareUpdate/dc7d105bda8ca7fc4bcb11fd3ea8371edb48a75bf91298ec5fcbef705c1e2c41.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/062-06892/3DF9328B-BC1D-451E-8810-84CE75087F09/com_apple_MobileAsset_SoftwareUpdate/a902ea9282aa0c0eac7b64c28a33c0a7bdab6a914b303e8ece4af92f084f99cf.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/062-06893/4CC0D872-5AEA-44C3-AA1C-AFF18EF5729D/com_apple_MobileAsset_SoftwareUpdate/b3c9f914a31afcb6a5226b124de4b72107f4d1cd9c00dd63a156ca94558948de.aea
https://appledb.dev/device/Apple-Watch-SE-3
https://updates.cdn-apple.com/2025FallFCS/mobileassets/052-85583/9BA90BDE-ACAC-4D16-93F4-2E09DBDA345D/com_apple_MobileAsset_SoftwareUpdate/ba38e58949116c28da9e114ac5e224163a6960e1beebc3c8b73a7b17972a147b.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/052-85574/5BF78F76-2180-4F08-B39F-C32AF4A7CCD0/com_apple_MobileAsset_SoftwareUpdate/8f80cc661f8570741fca061972f380cd8443da9c6d25b7689371fa7a3ff54edd.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/052-85570/8120DB59-B4AB-479D-8D92-CF718948EB29/com_apple_MobileAsset_SoftwareUpdate/95680bb2d0fe33d5fe080db1f2e43d4c2ee577c7c615207bcc688c7cdb8297a2.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/052-85592/873ACC09-83EC-4929-A9BD-523EDA999DFC/com_apple_MobileAsset_SoftwareUpdate/8896e021194f9234cdfff15d414536b52ffba4a6dcd483a69fda0bdafb0bcfbe.aea
https://updates.cdn-apple.com/2025FallFCS/mobileassets/082-84859/E6F8A64B-3D4B-4CDA-9392-B6D0F200E757/com_apple_MobileAsset_SoftwareUpdate/b8820fe324b7288b25660b88d18dc54159ea32e324aaedc237b8093b471d57db.aea
""".strip().splitlines()

def dynamic_zip(url: str):
    resp = SESSION.head(url, timeout=5)
    resp.raise_for_status()
    size = resp.headers.get("Content-Length")
    if size and int(size) < 1024 * 1024 * 10:
        return zipfile.ZipFile(io.BytesIO(SESSION.get(url, timeout=5).content))
    else:
        return remotezip.RemoteZip(url, session=SESSION)


def fetch_keys(file: Path, url: str, build_manifest: dict):
    build_number = build_manifest["ProductBuildVersion"]
    build_train = build_manifest["BuildIdentities"][0]["Info"]["BuildTrain"]
    product_types = build_manifest["SupportedProductTypes"]

    keys = {}

    for product_type in product_types:
        resp = SESSION.get(
            f"https://theapplewiki.com/wiki/Special:Ask/-5B-5B-2DHas-20subobject::Keys:{build_train}-20{build_number}-20({product_type})-5D-5D/-3FHas-20filename%3Dfilename/-3FHas-20firmware-20device%3Ddevice/-3FHas-20key%3Dkey/-3FKey-20DevKBAG%3Ddevkbag/-3FHas-20key-20IV%3Div/-3FKey-20KBAG%3Dkbag/mainlabel%3Dfilename/limit%3D100/offset%3D0/format%3Djson/searchlabel%3DKeys/type%3Dsimple"
        )
        resp.raise_for_status()
        data = resp.json()
        for key_info in data.values():
            assert len(key_info["filename"]) == 1, f"Multiple filenames: {key_info['filename']}"
            assert len(key_info["iv"]) <= 1, f"Multiple IVs: {key_info['iv']}"
            assert len(key_info["key"]) <= 1, f"Multiple keys: {key_info['key']}"

            filename = key_info["filename"][0]
            iv = next(iter(key_info["iv"]), None)
            key = next(iter(key_info["key"]), None)

            if iv == "Unknown":
                iv = None
            elif iv:
                iv = bytes.fromhex(iv)

            if key == "Unknown":
                key = None
            elif key:
                try:
                    key = bytes.fromhex(key)
                except ValueError:
                    key = base64.b64decode(key)

            info = {
                "iv": iv,
                "key": key,
            }

            if filename in keys:
                assert keys[filename] == info, f"Conflicting keys: {keys[filename]} vs {info}"
            keys[filename] = info

    return keys


def fetch_device_tree(url: str, zip: zipfile.ZipFile, root: Path, build_manifest_path: Path):
    save_dir = root / "device_trees"
    save_dir.mkdir(exist_ok=True)

    names = [name for name in zip.namelist() if "DeviceTree" in name and not name.endswith(".plist")]
    saved_paths: list[Path] = []
    for name in names:
        save_path = save_dir / Path(name).name
        assert not save_path.exists(), f"File already exists: {save_path}"
        save_path.write_bytes(zip.read(name))
        saved_paths.append(save_path)

    # Device trees require postprocessing, if IMG3 or encrypted IMG4

    build_manifest = None
    keys = None
    for saved_path in saved_paths:
        out_path = saved_path.with_suffix("")
        data = saved_path.read_bytes()
        if data[:4] == b"3gmI":
            # raise NotImplementedError("IMG3 device tree")
            if not keys:
                keys = fetch_keys(saved_path, url, plistlib.loads(build_manifest_path.read_bytes()))

            key = keys.get(saved_path.name)
            if not key:
                raise RuntimeError(f"Missing key for {saved_path.name}")
            subprocess.run(
                ["./oldimgtool/target/debug/oldimgtool", "--iv", key["iv"].hex(), "--key", key["key"].hex(), saved_path, out_path],
                check=True,
            )

            try:
                device_tree.parse_device_tree(out_path)
            except ValueError:
                raise RuntimeError(f"Invalid key for {saved_path.name}")

        else:
            try:
                im4p = pyimg4.IM4P(data)
                assert im4p.payload, "No payload found"
                if im4p.payload.encrypted:
                    # raise NotImplementedError("Encrypted IMG4 device tree")
                    if not keys:
                        keys = fetch_keys(saved_path, url, plistlib.loads(build_manifest_path.read_bytes()))
                    key = keys.get(saved_path.name)
                    if not key:
                        raise RuntimeError(f"Missing key for {saved_path.name}")
                    im4p.payload.decrypt(pyimg4.Keybag(iv=key["iv"], key=key["key"]))
                if im4p.payload.compression:
                    im4p.payload.decompress()
                out_path.write_bytes(im4p.payload.data)

                try:
                    device_tree.parse_device_tree(out_path)
                except ValueError:
                    raise RuntimeError(f"Invalid key for {saved_path.name}")
            except pyimg4.UnexpectedTagError as exc:
                raise NotImplementedError("Unknown device tree format") from exc

    return saved_paths


def fetch_restore(url: str, zip: zipfile.ZipFile, root: Path):
    save_path = root / "Restore.plist"

    restore_paths = [path for path in zip.namelist() if path.endswith("Restore.plist") and "BootabilityBundle" not in path]
    if len(restore_paths) == 0:
        # No Restore.plist found
        return
    assert len(restore_paths) == 1, f"Multiple Restore.plist found: {restore_paths}"
    save_path.write_bytes(zip.read(restore_paths[0]))

    return save_path


def fetch_manifest(url: str, zip: zipfile.ZipFile, root: Path):
    save_path = root / "BuildManifest.plist"

    if url.endswith(".ipsw"):
        # Try direct access first
        try:
            resp = SESSION.get(url[: url.rfind("/") + 1] + "BuildManifest.plist", timeout=5)
            resp.raise_for_status()
            save_path.write_bytes(resp.content)
            return save_path
        except (requests.Timeout, requests.HTTPError):
            pass

    # Try to extract from the zip
    manifest_paths = [path for path in zip.namelist() if path.endswith("BuildManifest.plist") and "BootabilityBundle" not in path]
    if len(manifest_paths) == 0:
        # No BuildManifest.plist found
        return
    assert len(manifest_paths) == 1, f"Multiple BuildManifest.plist found: {manifest_paths}"
    save_path.write_bytes(zip.read(manifest_paths[0]))

    return save_path


def fetch(url: str):
    cached_root = url_to_path(url)
    if cached_root.exists():
        return
    tmp_root = cached_root.with_suffix(".tmp")
    if tmp_root.exists():
        shutil.rmtree(tmp_root)
    tmp_root.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {url}")

    with dynamic_zip(url) as zip:
        restore = fetch_restore(url, zip, tmp_root)
        manifest = fetch_manifest(url, zip, tmp_root)
        dts = fetch_device_tree(url, zip, tmp_root, manifest)
        assert dts or restore or manifest, "No device tree, Restore.plist or BuildManifest.plist found"

    tmp_root.rename(cached_root)


if __name__ == "__main__":
    for url in urls:
        if not url.strip():
            continue
        if "appledb.dev" in url:
            continue
        fetch(url)
