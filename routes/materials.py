import json
import os

from fastapi import APIRouter, HTTPException, FastAPI, Query
from pymatgen.core import Structure
from pymatgen.io.cif import CifWriter
from starlette.responses import PlainTextResponse

from database import collection
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from bson import ObjectId
import pandas as pd
from fastapi.responses import FileResponse
from pymatgen.io.cif import CifParser

router = APIRouter()


# app = FastAPI()

# D:\Code\Dash-by-Plotly-master\sacada_pages_trial\et_carbon.csv
# 测试页面位于 http://127.0.0.1:8000/docs#/
# http://127.0.0.1:8000/api/materials
# http://127.0.0.1:8000/api/material/671e1961ab159a6f6ac9fddb
# http://127.0.0.1:8000/api/download
# http://127.0.0.1:8000/api/download/671e1961ab159a6f6ac9fdd6
# http://127.0.0.1:8000/api/download/671e1961ab159a6f6ac9fdfd

# 定义返回数据模型
# 用于解析 opt 与 scf 部分（字段类似，可根据需要合并或拆分）
class VaspInput(BaseModel):
    INCAR: Optional[str] = None
    KPOINTS: Optional[str] = None
    CONTCAR: Optional[str] = None


# elastic 里的 prop_data
class ElasticPropData(BaseModel):
    # stiffness_tensor: Optional[List[List[float]]] = None
    # compliance_tensor: Optional[List[List[float]]] = None
    Pugh_ratio: Optional[float] = None
    Cauchy_Pressure: Optional[float] = None
    Kleinman_parameter: Optional[float] = None
    Universal_Elastic_Anisotropy: Optional[float] = None
    Chung_Buessem_Anisotropy: Optional[float] = None
    Isotropic_Poissons_Ratio: Optional[float] = None
    Longitudinal_wave_velocity: Optional[float] = None
    Transverse_wave_velocity: Optional[float] = None
    Average_wave_velocity: Optional[float] = None
    Debye_temperature: Optional[float] = None
    stability: Optional[bool] = None
    anisotropic_mechanical_properties: Optional[Dict[str, Any]] = None
    average_mechanical_properties: Optional[Dict[str, Any]] = None
    average_youngs_modulus: Optional[float] = None


# elastic 部分
class ElasticData(BaseModel):
    INCAR: Optional[str] = None
    KPOINTS: Optional[str] = None
    ELASTIC_TENSOR: Optional[str] = None
    prop_data: Optional[ElasticPropData] = None


# band 部分
class BandGap(BaseModel):
    Band_Character: Optional[str] = Field(None, alias="Band Character")
    Band_Gap_eV: Optional[float] = Field(None, alias="Band Gap (eV)")
    Eigenvalue_of_VBM_eV: Optional[float] = Field(None, alias="Eigenvalue of VBM (eV)")
    Eigenvalue_of_CBM_eV: Optional[float] = Field(None, alias="Eigenvalue of CBM (eV)")
    Fermi_Energy_eV: Optional[float] = Field(None, alias="Fermi Energy (eV)")
    HOMO_LUMO_Bands: Optional[List[int]] = Field(None, alias="HOMO & LUMO Bands")
    Location_of_VBM: Optional[List[float]] = Field(None, alias="Location of VBM")
    Location_of_CBM: Optional[List[float]] = Field(None, alias="Location of CBM")


class BandData(BaseModel):
    band_gap: Optional[BandGap] = None
    Klabels: Optional[Dict[str, float]] = None


# metadata 部分
class Metadata(BaseModel):
    opt: Optional[VaspInput] = None
    scf: Optional[VaspInput] = None
    elastic: Optional[ElasticData] = None
    band: Optional[BandData] = None


class MaterialData(BaseModel):
    _id: Optional[str] = None
    sacada_id: Optional[str] = None
    structure: Optional[Dict[str, Any]] = None
    metadata: Optional[Metadata] = None
    formula: Optional[str] = None
    reduced_formula: Optional[str] = None
    crystal_system: Optional[str] = None
    space_group_symbol: Optional[str] = None
    Sites: Optional[int] = None


class MaterialSummary(BaseModel):
    _id: Optional[str] = None
    sacada_id: Optional[str] = None
    formula: Optional[str] = None
    reduced_formula: Optional[str] = None
    crystal_system: Optional[str] = None
    space_group_symbol: Optional[str] = None
    Sites: Optional[int] = None


@router.get("/material/{material_id}", response_model=MaterialData)
async def get_material_by_id(material_id: str):
    # 查询 MongoDB（假设 collection 已定义）
    object_id = ObjectId(material_id)
    doc = collection.find_one({"_id": object_id})
    if doc:
        # 将 _id 转为字符串，如果 _id 为 {"$oid": "..."} 则提取内部字符串
        if isinstance(doc.get("_id"), dict) and "$oid" in doc["_id"]:
            doc["_id"] = doc["_id"]["$oid"]
        else:
            doc["_id"] = str(doc["_id"])
        # 使用 Pydantic 的 parse_obj 来构建 MaterialData 对象
        try:
            material_data = MaterialData.parse_obj(doc)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data parsing error: {e}")
        return material_data
    else:
        raise HTTPException(status_code=404, detail="Material not found")


@router.get("/opt/{material_id}", response_class=PlainTextResponse)
async def get_opt_by_id(material_id: str):
    # 查询 MongoDB（假设 collection 已定义）
    object_id = ObjectId(material_id)
    doc = collection.find_one({"_id": object_id})
    if doc:
        # 将 _id 转为字符串，如果 _id 为 {"$oid": "..."} 则提取内部字符串
        if isinstance(doc.get("_id"), dict) and "$oid" in doc["_id"]:
            doc["_id"] = doc["_id"]["$oid"]
        else:
            doc["_id"] = str(doc["_id"])
        # 使用 Pydantic 的 parse_obj 来构建 MaterialData 对象
        try:
            opt_data = doc.get("metadata", {}).get("opt", {})
            # print(opt_data)
            INCAR = opt_data.get("INCAR")
            KPOINTS = opt_data.get("KPOINTS")
            CONTCAR = opt_data.get("CONTCAR")
            # 将内容合并为纯文本，可以根据需要调整格式
            combined_text = (
                f"INCAR:\n{INCAR}"
                f"KPOINTS:\n{KPOINTS}"
                f"CONTCAR:\n{CONTCAR}"
            )
            return combined_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data parsing error: {e}")
    else:
        raise HTTPException(status_code=404, detail="Material not found")


# @router.get("/opt/{material_id}/incar_file")
# async def get_incar_file(material_id: str):
#     object_id = ObjectId(material_id)
#     doc = collection.find_one({"_id": object_id})
#
#     if doc:
#         incar_data = doc.get("metadata", {}).get("opt", {}).get("INCAR", "")
#
#         # 将数据写入临时文件
#         incar_file_path = "/tmp/INCAR"
#         with open(incar_file_path, "w", encoding="utf-8") as f:
#             f.write(incar_data)
#
#         return FileResponse(incar_file_path, filename="INCAR.txt", media_type="text/plain")
#     else:
#         raise HTTPException(status_code=404, detail="Material not found")


@router.get("/scf/{material_id}", response_class=PlainTextResponse)
async def get_scf_by_id(material_id: str):
    # 查询 MongoDB（假设 collection 已定义）
    object_id = ObjectId(material_id)
    doc = collection.find_one({"_id": object_id})
    if doc:
        # 将 _id 转为字符串，如果 _id 为 {"$oid": "..."} 则提取内部字符串
        if isinstance(doc.get("_id"), dict) and "$oid" in doc["_id"]:
            doc["_id"] = doc["_id"]["$oid"]
        else:
            doc["_id"] = str(doc["_id"])
        # 使用 Pydantic 的 parse_obj 来构建 MaterialData 对象
        try:
            opt_data = doc.get("metadata", {}).get("scf", {})
            # print(opt_data)
            INCAR = opt_data.get("INCAR")
            KPOINTS = opt_data.get("KPOINTS")
            CONTCAR = opt_data.get("CONTCAR")
            # 将内容合并为纯文本，可以根据需要调整格式
            combined_text = (
                f"INCAR:\n{INCAR}"
                f"KPOINTS:\n{KPOINTS}"
                f"CONTCAR:\n{CONTCAR}"
            )
            return combined_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data parsing error: {e}")
    else:
        raise HTTPException(status_code=404, detail="Material not found")


@router.get("/elastic/{material_id}", response_class=PlainTextResponse)
async def get_elastic_by_id(material_id: str):
    # 查询 MongoDB（假设 collection 已定义）
    object_id = ObjectId(material_id)
    doc = collection.find_one({"_id": object_id})
    if doc:
        # 将 _id 转为字符串，如果 _id 为 {"$oid": "..."} 则提取内部字符串
        if isinstance(doc.get("_id"), dict) and "$oid" in doc["_id"]:
            doc["_id"] = doc["_id"]["$oid"]
        else:
            doc["_id"] = str(doc["_id"])
        # 使用 Pydantic 的 parse_obj 来构建 MaterialData 对象
        try:
            elastic_data = doc.get("metadata", {}).get("elastic", {})
            # print(opt_data)
            INCAR = elastic_data.get("INCAR")
            KPOINTS = elastic_data.get("KPOINTS")
            ELASTIC_TENSOR = elastic_data.get("ELASTIC_TENSOR")
            stiffness_tensor = elastic_data.get("prop_data", {}).get("stiffness_tensor")
            compliance_tensor = elastic_data.get("prop_data", {}).get("compliance_tensor")
            # 将内容合并为纯文本，可以根据需要调整格式
            combined_text = (
                f"INCAR:\n{INCAR}"
                f"KPOINTS:\n{KPOINTS}"
                f"ELASTIC_TENSOR:\n{ELASTIC_TENSOR}"
                f"STIFFNESS_TENSOR:\n{stiffness_tensor}\n"
                f"COMPLIANCE_TENSOR:\n{compliance_tensor}"
            )
            return combined_text
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data parsing error: {e}")
    else:
        raise HTTPException(status_code=404, detail="Material not found")


@router.get("/ElasticProp/{material_id}", response_model=ElasticPropData)
async def get_elasticprop_by_id(material_id: str):
    # 查询 MongoDB（假设 collection 已定义）
    object_id = ObjectId(material_id)
    doc = collection.find_one({"_id": object_id})
    if doc:
        # 将 _id 转为字符串，如果 _id 为 {"$oid": "..."} 则提取内部字符串
        if isinstance(doc.get("_id"), dict) and "$oid" in doc["_id"]:
            doc["_id"] = doc["_id"]["$oid"]
        else:
            doc["_id"] = str(doc["_id"])
        # 使用 Pydantic 的 parse_obj 来构建 MaterialData 对象
        try:
            prop_data = doc.get("metadata", {}).get("elastic", {}).get("prop_data", {})
            # 删除 stiffness_tensor 和 compliance_tensor
            prop_data.pop("stiffness_tensor", None)
            prop_data.pop("compliance_tensor", None)
            return prop_data
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data parsing error: {e}")
        # return elastic_data
    else:
        raise HTTPException(status_code=404, detail="Material not found")


@router.get("/band/{material_id}", response_model=BandGap)
async def get_band_by_id(material_id: str):
    # 查询 MongoDB
    object_id = ObjectId(material_id)
    doc = collection.find_one({"_id": object_id})

    if doc:
        # 处理 _id
        if isinstance(doc.get("_id"), dict) and "$oid" in doc["_id"]:
            doc["_id"] = doc["_id"]["$oid"]
        else:
            doc["_id"] = str(doc["_id"])

        try:
            band_data = doc.get("metadata", {}).get("band", {})

            # 确保 band_gap 是一个字典
            band_gap_data = band_data.get("band_gap", {})
            if not isinstance(band_gap_data, dict):
                band_gap_data = {}

            # # 确保 Klabels 是一个字典
            # klabels_data = band_data.get("Klabels", {})
            # if not isinstance(klabels_data, dict):
            #     klabels_data = {}

            # 解析数据并返回
            return BandGap.parse_obj(band_gap_data)

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data parsing error: {e}")

    else:
        raise HTTPException(status_code=404, detail="Material not found")


@router.get("/material_basicprop/{material_id}", response_model=MaterialSummary)
async def get_material_basicprop_by_id(material_id: str):
    # 查询 MongoDB（假设 collection 已定义）
    object_id = ObjectId(material_id)
    doc = collection.find_one({"_id": object_id})

    if doc:
        # 处理 _id
        doc["_id"] = str(doc["_id"])

        # 过滤掉 structure 和 metadata
        filtered_data = {k: v for k, v in doc.items() if k not in ["structure", "metadata"]}
        try:
            material_basicprop = MaterialSummary.parse_obj(filtered_data)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Data parsing error: {e}")

        return material_basicprop
    else:
        raise HTTPException(status_code=404, detail="Material not found")


def get_material_from_db():
    materials = []
    for doc in collection.find():
        doc["_id"] = str(doc["_id"])
        print(doc)
        materials.append(MaterialData(data=doc))
    return materials


@router.get("/materials", response_model=List[MaterialData])
async def get_materials():
    return get_material_from_db()


@router.get("/materials_summary")
async def get_materials(page: int = Query(1, alias="page")):
    items_per_page = 10
    materials = list(
        collection.find({}, {"_id": 1, "formula": 1, "reduced_formula": 1, "crystal_system": 1,
                             "space_group_symbol": 1, "Sites": 1})
        .skip((page - 1) * items_per_page)
        .limit(items_per_page))
    total_items = collection.count_documents({})
    total_pages = (total_items + items_per_page - 1) // items_per_page  # 计算总页
    # 确保 `_id` 转换为字符串格式
    for material in materials:
        material["_id"] = str(material["_id"])
    return {"materials": materials, "total_pages": total_pages}


import plotly.express as px
import json


@router.get("/charts")
async def update_charts():
    df_display = pd.DataFrame(list(collection.find({}, {"crystal_system": 1, "space_group_symbol": 1, "Sites": 1})))

    # Crystal System Pie Chart
    crystal_pie = px.pie(df_display, names="crystal_system", title="Distribution of Crystal Systems")

    # Top 20 Space Group Symbols Pie Chart
    top_20_space_groups = df_display["space_group_symbol"].value_counts().nlargest(20).index
    filtered_df = df_display[df_display["space_group_symbol"].isin(top_20_space_groups)]
    space_group_pie = px.pie(filtered_df, names="space_group_symbol", title="Top 20 Space Group Symbols")

    # Sites Histogram
    sites_hist = px.histogram(df_display, x="Sites", nbins=10, title="Distribution of Materials by Sites",
                              marginal="box")

    response = {
        "crystal_pie": json.loads(crystal_pie.to_json()),
        "space_group_pie": json.loads(space_group_pie.to_json()),
        "sites_hist": json.loads(sites_hist.to_json())
    }

    return response  # ✅ 确保是 JSON 格式，而不是字符串


# @router.get("/material/{material_id}")
# async def get_material_by_id(material_id: str):
#     from bson import ObjectId
#     object_id = ObjectId(material_id)
#     doc = collection.find_one({"_id": object_id})
#     if doc:
#         print(doc)
#         doc["_id"] = str(doc["_id"])
#         return MaterialData(data=doc)
#     else:
#         raise HTTPException(status_code=404, detail="Material not found")


@router.get("/download")
async def download_csv():
    # df = pd.read_csv("static/et_carbon.csv")
    df_file_path = "static/et_carbon.csv"
    df_file_name = "et_carbon.csv"
    return FileResponse(df_file_path, filename=df_file_name, media_type="text/csv")


@router.get("/download/{material_id}")
async def download_structure_by_id(material_id: str):
    doc = collection.find_one(ObjectId(material_id))
    if not doc:
        raise HTTPException(status_code=404, detail="Material not found")
    structure_dict = doc.get("structure")
    if not structure_dict:
        raise HTTPException(status_code=404, detail="Structure data not found")
    try:
        structure = Structure.from_dict(structure_dict)
        structure_cif = CifWriter(structure, significant_figures=6)
        print(structure_cif)
        cif_filename = f"{material_id}.cif"
        structure_cif.write_file(f'{str(material_id)}.cif')
        structure_json = json.dumps(structure.as_dict(), indent=2)
        structure.to(fmt="cif")
        # structure.to(filename=cif_filename, fmt="cif")
        # return {"message": "Structure data retrieved", "structure": structure_json}
        return FileResponse(cif_filename, filename=cif_filename, media_type="chemical/x-cif")
        # return FileResponse(structure.to(fmt="cif"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing structure: {str(e)}")


