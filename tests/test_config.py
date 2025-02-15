import pytest
import os
import yaml
from src.osint.framework import ConfigManager, OSINTFramework

# Fixture for temporary configuration file
@pytest.fixture
def test_config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config = {
        'api_keys': {
            'shodan': 'test-shodan-key',
            'virustotal': 'test-vt-key',
            'censys': 'test-censys-key'
        },
        'modules': {
            'passive_recon': True,
            'active_recon': True,
            'social_media': True,
            'dark_web': False
        },
        'scan_options': {
            'timeout': 30,
            'threads': 5,
            'max_subdomains': 100
        },
        'output': {
            'format': 'json',
            'directory': str(tmp_path / 'results')
        }
    }
    
    config_path = tmp_path / "test_config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config, f)
    
    return config_path

class TestConfigManager:
    def test_config_loading(self, test_config_file):
        """Test that configuration loads correctly."""
        config_manager = ConfigManager(str(test_config_file))
        assert config_manager.config is not None
        assert isinstance(config_manager.config, dict)
    
    def test_default_config_creation(self, tmp_path):
        """Test that default configuration is created if none exists."""
        config_path = tmp_path / "nonexistent_config.yaml"
        config_manager = ConfigManager(str(config_path))
        
        assert os.path.exists(config_path)
        assert config_manager.config['modules']['passive_recon'] is True
    
    def test_api_key_retrieval(self, test_config_file):
        """Test API key retrieval functionality."""
        config_manager = ConfigManager(str(test_config_file))
        
        assert config_manager.get_api_key('shodan') == 'test-shodan-key'
        assert config_manager.get_api_key('nonexistent') == ''
    
    def test_module_configuration(self, test_config_file):
        """Test module configuration settings."""
        config_manager = ConfigManager(str(test_config_file))
        
        assert config_manager.config['modules']['passive_recon'] is True
        assert config_manager.config['modules']['dark_web'] is False
    
    def test_scan_options(self, test_config_file):
        """Test scan option settings."""
        config_manager = ConfigManager(str(test_config_file))
        
        assert config_manager.config['scan_options']['timeout'] == 30
        assert config_manager.config['scan_options']['threads'] == 5

class TestOSINTFramework:
    def test_framework_initialization(self, test_config_file):
        """Test framework initialization with configuration."""
        framework = OSINTFramework(str(test_config_file))
        
        assert framework.config is not None
        assert framework.results_manager is not None
        assert len(framework.modules) > 0
    
    def test_module_loading(self, test_config_file):
        """Test that modules are loaded based on configuration."""
        framework = OSINTFramework(str(test_config_file))
        
        # Count enabled modules
        enabled_modules = sum(1 for module in framework.modules 
                            if framework.config.config['modules'][module.module_name])
        
        assert len(framework.modules) == enabled_modules

def test_results_directory_creation(test_config_file):
    """Test that results directory is created."""
    framework = OSINTFramework(str(test_config_file))
    results_dir = framework.config.config['output']['directory']
    
    assert os.path.exists(results_dir)
    assert os.path.isdir(results_dir)

if __name__ == '__main__':
    pytest.main([__file__])