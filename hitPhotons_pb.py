# coding: utf-8
from cprotobuf import ProtoEntity, Field
# file: photonHit.proto
class Photon(ProtoEntity):
    # enum OriginFlag
    CHERENKOV=0
    SCINTILLATION=1
    REEMISSION=2
    CHROMA=3
    PMTID           = Field('int32',	1, required=False)
    Time            = Field('double',	2, required=False)
    KineticEnergy   = Field('double',	3, required=False)
    posX            = Field('double',	4, required=False)
    posY            = Field('double',	5, required=False)
    posZ            = Field('double',	6, required=False)
    momX            = Field('double',	7, required=False)
    momY            = Field('double',	8, required=False)
    momZ            = Field('double',	9, required=False)
    polX            = Field('double',	10, required=False)
    polY            = Field('double',	11, required=False)
    polZ            = Field('double',	12, required=False)
    trackID         = Field('int32',	14, required=False)
    origin          = Field('enum',	15, required=False)

class PhotonHits(ProtoEntity):
    count           = Field('int32',	1, required=False)
    photon          = Field(Photon,	2, repeated=True)

