"""
Narrative Loader - Carga la narrativa desde archivos externos JSON.
Permite modificar la historia del juego sin editar código.
"""
import json
import os
from pathlib import Path

class NarrativeLoader:
    _instance = None
    _data = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load()
        return cls._instance
    
    def _load(self):
        """Carga el archivo de narrativa."""
        base_dir = Path(__file__).parent.parent
        narrative_path = base_dir / "data" / "narrative.json"
        
        if narrative_path.exists():
            with open(narrative_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        else:
            self._data = None
            print(f"Warning: Narrative file not found at {narrative_path}")
    
    def reload(self):
        """Recarga el archivo de narrativa."""
        self._load()
    
    @property
    def encounters(self):
        """Retorna el diccionario de encuentros."""
        if self._data:
            return self._data.get('encounters', {})
        return {}
    
    @property
    def hitchhiker_templates(self):
        """Retorna las plantillas de autoestopistas."""
        if self._data:
            return self._data.get('hitchhikers', [])
        return []
    
    @property
    def locations(self):
        """Retorna las ubicaciones."""
        if self._data:
            return self._data.get('locations', {})
        return {}
    
    def get_encounter(self, key):
        """Obtiene un encuentro por su clave."""
        if self._data:
            return self._data.get('encounters', {}).get(key)
        return None
    
    def get_hitchhiker_template(self, name):
        """Obtiene una plantilla de autoestopista por nombre."""
        if self._data:
            for template in self._data.get('hitchhikers', []):
                if template.get('name') == name:
                    return template
        return None
    
    def get_biome_encounters(self, biome):
        """Obtiene los encuentros disponibles para un bioma."""
        if self._data:
            biomes = self._data.get('locations', {}).get('biomes', {})
            return biomes.get(biome, {}).get('encounters', [])
        return []


# Instancia global
narrative = NarrativeLoader()