"""
模板注册表：自动扫描 templates/ 下所有含 template.py 的子目录
"""
import importlib
import importlib.util
from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent


def list_templates() -> list[dict]:
    """返回所有可用模板的 TEMPLATE_INFO"""
    templates = []
    for d in sorted(TEMPLATES_DIR.iterdir()):
        if d.is_dir() and (d / "template.py").exists():
            mod = _import_template(d.name)
            if mod and hasattr(mod, "TEMPLATE_INFO"):
                templates.append(mod.TEMPLATE_INFO)
    return templates


def get_template(name: str):
    """按名称加载模板模块，返回模块对象（含 generate_poster 函数）"""
    mod = _import_template(name)
    if mod is None:
        available = [d.name for d in TEMPLATES_DIR.iterdir()
                     if d.is_dir() and (d / "template.py").exists()]
        raise ValueError(f"模板 '{name}' 不存在。可用模板: {available}")
    return mod


def _import_template(name: str):
    """动态导入 templates/<name>/template.py"""
    template_dir = TEMPLATES_DIR / name
    if not (template_dir / "template.py").exists():
        return None
    module_name = f"templates.{name}.template"
    try:
        return importlib.import_module(module_name)
    except ImportError:
        spec = importlib.util.spec_from_file_location(
            module_name, template_dir / "template.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
