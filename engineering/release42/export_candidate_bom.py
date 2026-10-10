"""Export the actual candidate BOM without inventing unspecified ordering codes."""
from pathlib import Path
import csv,xml.etree.ElementTree as ET
root=Path('engineering/release42')
nl=ET.parse(root/'candidate_netlist.xml').getroot()
known={'C9':('Panasonic','10SVPC120M','Manufacturer C6 land pattern applied'),
       'C13':('Panasonic','EEH-ZA1H470P','SMD hybrid reservoir'),
       'L1':('Coilcraft','XAL8080-333MED','33 uH; manufacturer electrical data reviewed'),
       'R10':('Vishay','WSLP2512L5000FEA','Kelvin pickup/current sharing review remains open'),
       'R11':('Vishay','WSLP2512L5000FEA','Kelvin pickup/current sharing review remains open')}
with (root/'candidate_BOM_REVIEW.csv').open('w',newline='',encoding='utf-8') as out:
    w=csv.writer(out);w.writerow(['Reference','Schematic value','Footprint','Manufacturer','Verified ordering code','Status','Notes'])
    for c in sorted(nl.find('components'),key=lambda c:c.attrib['ref']):
        ref=c.attrib['ref'];value=c.findtext('value','');footprint=c.findtext('footprint','')
        manufacturer,mpn,note=known.get(ref,('','','Exact ordering code/assembly specification requires BOM review'))
        if ref=='D2':note='Existing SMCJ28CA; 4S clamp selection and pulse-current path not qualified'
        if ref in ('C1','C2','C10'):note='Exact MLCC and effective capacitance under DC bias must be verified'
        if ref=='BEC1':note='External Pi BEC; PCB /5V_PI connection is a test-point branch, not the 5 A load path'
        w.writerow([ref,value,footprint,manufacturer,mpn,'NOT RELEASED',note])
print('Exported candidate BOM review; unspecified ordering codes remain blank')
