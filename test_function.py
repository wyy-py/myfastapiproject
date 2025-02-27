from pydantic import BaseModel
from pymongo import MongoClient
from typing import Dict, Any
from bson import ObjectId


class MaterialData(BaseModel):
    data: Dict[str, Any]  # 结构信息，存储 JSON
    # metadata: Dict[str, Any]  # 额外的材料数据
    # cif_data: str  # 存储 CIF 文件路径


def get_material_from_db():
    client = MongoClient("mongodb://localhost:27017/")
    db = client["carbon_et"]
    collection = db["stable_structures"]
    materials = []
    for doc in collection.find():
        print(doc)
        materials.append(MaterialData(data=doc))
    return materials


get_material_from_db()
# _id=str(doc["_id"]),
#             band_gap=doc.get("metadata", {}).get("band", {}).get("band_gap", {}).get("Band Gap (eV)"),
#             youngs_modulus=doc.get("metadata", {}).get("elastic", {}).get("prop_data", {}).get("average_youngs_modulus"),
#             # cif_data=f"cif_data/{doc['_id']}.cif"  # 假设 CIF 文件存放在 static 目录
