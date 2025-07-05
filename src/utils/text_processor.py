from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Protocol, Union, Optional, Dict, Any, List, Callable
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import time
from functools import wraps
import pickle
import hashlib
import logging

logger = logging.getLogger(__name__)
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

class ProcessingLevel(Enum):
    LIGHT = "light"
    STANDARD = "standard"
    AGGRESSIVE = "aggressive"
    CUSTOM = "custom"

@dataclass
class ProcessingConfig:
    """Immutable configuration for text processing pipeline."""
    level: ProcessingLevel = ProcessingLevel.STANDARD
    preserve_brackets: bool = False
    preserve_currency: bool = True
    preserve_urls: bool = True
    preserve_emails: bool = True
    preserve_hashtags: bool = True
    preserve_mentions: bool = True
    expand_contractions: bool = True
    normalize_unicode: bool = True
    remove_html: bool = True
    remove_extra_whitespace: bool = True
    language: str = 'en'
    custom_patterns: Dict[str, str] = None
    max_text_length: int = 1_000_000
    enable_caching: bool = True
    cache_size: int = 1000
    
    def __post_init__(self):
        if self.custom_patterns is None:
            self.custom_patterns = {}

class ProcessingStep(ABC):
    """Abstract base class for processing steps."""
    
    @abstractmethod
    def process(self, text: str, config: ProcessingConfig) -> str:
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        pass

# Placeholder ProcessingStep implementations
class LowercaseStep(ProcessingStep):
    def process(self, text: str, config: ProcessingConfig) -> str:
        return text.lower()
    
    def get_name(self) -> str:
        return "LowercaseStep"

class StripWhitespaceStep(ProcessingStep):
    def process(self, text: str, config: ProcessingConfig) -> str:
        return text.strip()
    
    def get_name(self) -> str:
        return "StripWhitespaceStep"

class TextMetrics:
    """Comprehensive text metrics and statistics."""
    
    def __init__(self, original_text: str, processed_text: str, 
                 processing_time: float, steps_applied: List[str]):
        self.original_length = len(original_text)
        self.processed_length = len(processed_text)
        self.compression_ratio = self.processed_length / self.original_length if self.original_length > 0 else 0
        self.processing_time = processing_time
        self.steps_applied = steps_applied
        self.characters_removed = self.original_length - self.processed_length
        
        # Advanced metrics
        self.word_count_original = len(original_text.split())
        self.word_count_processed = len(processed_text.split())
        self.avg_word_length = sum(len(word) for word in processed_text.split()) / len(processed_text.split()) if processed_text.split() else 0
        
    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_length': self.original_length,
            'processed_length': self.processed_length,
            'compression_ratio': self.compression_ratio,
            'processing_time': self.processing_time,
            'characters_removed': self.characters_removed,
            'word_count_original': self.word_count_original,
            'word_count_processed': self.word_count_processed,
            'avg_word_length': self.avg_word_length,
            'steps_applied': self.steps_applied
        }

class ProcessingResult:
    """Container for processing results with metadata."""
    
    def __init__(self, text: str, metrics: TextMetrics, 
                 features: Dict[str, Any] = None, errors: List[str] = None):
        self.text = text
        self.metrics = metrics
        self.features = features or {}
        self.errors = errors or []
        self.success = len(self.errors) == 0
        
    def __str__(self) -> str:
        return f"ProcessingResult(length={len(self.text)}, success={self.success})"

def performance_monitor(func):
    """Decorator to monitor processing performance."""
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        try:
            result = func(self, *args, **kwargs)
            processing_time = time.time() - start_time
            self._update_performance_stats(func.__name__, processing_time, True)
            return result
        except Exception as e:
            processing_time = time.time() - start_time
            self._update_performance_stats(func.__name__, processing_time, False)
            raise
    return wrapper

class CacheManager:
    """LRU cache for processed texts."""
    
    def __init__(self, max_size: int = 1000):
        self.max_size = max_size
        self.cache = {}
        self.access_order = []
    
    def _get_key(self, text: str, config: ProcessingConfig) -> str:
        """Generate cache key from text and config."""
        config_str = str(sorted(config.__dict__.items()))
        return hashlib.md5(f"{text}{config_str}".encode()).hexdigest()
    
    def get(self, text: str, config: ProcessingConfig) -> Optional[ProcessingResult]:
        key = self._get_key(text, config)
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, text: str, config: ProcessingConfig, result: ProcessingResult):
        key = self._get_key(text, config)
        
        # Remove oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            oldest_key = self.access_order.pop(0)
            del self.cache[oldest_key]
        
        self.cache[key] = result
        if key not in self.access_order:
            self.access_order.append(key)
        
    def clear(self):
        self.cache.clear()
        self.access_order.clear()
        
    def stats(self) -> Dict[str, Any]:
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hit_ratio': getattr(self, '_hits', 0) / max(getattr(self, '_total_requests', 1), 1)
        }

class TextProcessor:
    """
    Enterprise-grade text processor with advanced features:
    - Configurable processing pipelines
    - Performance monitoring
    - Caching
    - Batch processing
    - Async support
    - Comprehensive metrics
    """
    
    def __init__(self, config: ProcessingConfig = None):
        self.config = config or ProcessingConfig()
        self.cache = CacheManager(self.config.cache_size) if self.config.enable_caching else None
        self.performance_stats = {}
        self.processing_steps = self._initialize_steps()
        
    def _initialize_steps(self) -> List[ProcessingStep]:
        """Initialize processing steps based on configuration."""
        # This would contain your concrete step implementations
        # For brevity, showing structure only
        steps = []
        if self.config.level == ProcessingLevel.STANDARD:
            steps.append(LowercaseStep())
            steps.append(StripWhitespaceStep())
        # Add more steps based on config.level or custom_patterns
        return steps
    
    def _update_performance_stats(self, operation: str, time_taken: float, success: bool):
        """Update performance monitoring statistics."""
        if operation not in self.performance_stats:
            self.performance_stats[operation] = {
                'total_calls': 0,
                'total_time': 0,
                'success_count': 0,
                'error_count': 0,
                'avg_time': 0
            }
        
        stats = self.performance_stats[operation]
        stats['total_calls'] += 1
        stats['total_time'] += time_taken
        stats['avg_time'] = stats['total_time'] / stats['total_calls']
        
        if success:
            stats['success_count'] += 1
        else:
            stats['error_count'] += 1
    
    @performance_monitor
    def process(self, text: str, config: ProcessingConfig = None) -> ProcessingResult:
        """Process single text with comprehensive error handling and metrics."""
        config = config or self.config
        
        # Validation
        if not isinstance(text, str):
            raise ValueError(f"Input must be string, got {type(text)}")
        
        if len(text) > config.max_text_length:
            raise ValueError(f"Text too long: {len(text)} > {config.max_text_length}")
        
        # Check cache
        if self.cache and config.enable_caching:
            cached_result = self.cache.get(text, config)
            if cached_result:
                return cached_result
        
        start_time = time.time()
        original_text = text
        steps_applied = []
        errors = []
        
        try:
            # Apply processing steps
            for step in self.processing_steps:
                try:
                    text = step.process(text, config)
                    steps_applied.append(step.get_name())
                except Exception as e:
                    errors.append(f"Step {step.get_name()} failed: {str(e)}")
                    if config.level == ProcessingLevel.AGGRESSIVE:
                        continue  # Skip failed steps in aggressive mode
                    else:
                        raise
            
            processing_time = time.time() - start_time
            metrics = TextMetrics(original_text, text, processing_time, steps_applied)
            
            # Extract features
            features = self._extract_advanced_features(text, config)
            
            result = ProcessingResult(text, metrics, features, errors)
            
            # Cache result
            if self.cache and config.enable_caching:
                self.cache.set(original_text, config, result)
            
            return result
            
        except Exception as e:
            processing_time = time.time() - start_time
            metrics = TextMetrics(original_text, text, processing_time, steps_applied)
            return ProcessingResult(text, metrics, {}, [str(e)])
    
    def process_batch(self, texts: List[str], config: ProcessingConfig = None, 
                     max_workers: int = None) -> List[ProcessingResult]:
        """Process multiple texts in parallel."""
        config = config or self.config
        max_workers = max_workers or min(32, len(texts))
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(self.process, text, config) for text in texts]
            return [future.result() for future in futures]
    
    async def process_async(self, text: str, config: ProcessingConfig = None) -> ProcessingResult:
        """Async version of process method."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.process, text, config)
    
    def _extract_advanced_features(self, text: str, config: ProcessingConfig) -> Dict[str, Any]:
        """Extract comprehensive features from processed text."""
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]
        
        return {
            # Basic metrics
            'char_count': len(text),
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_word_length': sum(len(w) for w in words) / len(words) if words else 0,
            'avg_sentence_length': sum(len(s.split()) for s in sentences) / len(sentences) if sentences else 0,
            
            # Character distribution
            'digit_ratio': sum(c.isdigit() for c in text) / len(text) if text else 0,
            'upper_ratio': sum(c.isupper() for c in text) / len(text) if text else 0,
            'lower_ratio': sum(c.islower() for c in text) / len(text) if text else 0,
            'space_ratio': sum(c.isspace() for c in text) / len(text) if text else 0,
            'punct_ratio': sum(not c.isalnum() and not c.isspace() for c in text) / len(text) if text else 0,
            
            # Content indicators
            'has_urls': 'http' in text.lower() or 'www.' in text.lower(),
            'has_emails': '@' in text and '.' in text,
            'has_hashtags': '#' in text,
            'has_mentions': '@' in text,
            'has_currency': any(symbol in text for symbol in ['$', '€', '£', '¥']),
            'has_numbers': any(c.isdigit() for c in text),
            
            # Language indicators
            'language': config.language,
            'estimated_reading_time': len(words) / 200 if words else 0,  # ~200 WPM
            
            # Quality metrics
            'is_empty': not bool(text.strip()),
            'is_meaningful': len(words) > 2 and any(len(w) > 3 for w in words),
            'complexity_score': len(set(words)) / len(words) if words else 0,  # Unique word ratio
        }
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance statistics."""
        return {
            'processing_stats': self.performance_stats,
            'cache_stats': self.cache.stats() if self.cache else None,
            'total_processed': sum(stats['total_calls'] for stats in self.performance_stats.values()),
            'total_errors': sum(stats['error_count'] for stats in self.performance_stats.values()),
            'overall_success_rate': (
                sum(stats['success_count'] for stats in self.performance_stats.values()) /
                max(sum(stats['total_calls'] for stats in self.performance_stats.values()), 1)
            )
        }
    
    def reset_stats(self):
        """Reset all performance statistics."""
        self.performance_stats.clear()
        if self.cache:
            self.cache.clear()
    
    def export_config(self, filepath: str):
        """Export current configuration to file."""
        with open(filepath, 'wb') as f:
            pickle.dump(self.config, f)
    
    @classmethod
    def load_config(cls, filepath: str) -> 'TextProcessorV2':
        """Load processor with configuration from file."""
        with open(filepath, 'rb') as f:
            config = pickle.load(f)
        return cls(config)

# Example usage showing the enhanced capabilities
if __name__ == "__main__":
    # Custom configuration
    config = ProcessingConfig(
        level=ProcessingLevel.STANDARD,
        preserve_brackets=False,
        preserve_currency=True,
        language='en',
        enable_caching=True,
        cache_size=500
    )
    
    processor = TextProcessorV2(config)
    
    # Single text processing
    result = processor.process("Hello world! This is a test (ignore this).")
    print(f"Processed: {result.text}")
    print(f"Metrics: {result.metrics.to_dict()}")
    print(f"Features: {result.features}")
    
    # Batch processing
    texts = ["Text 1", "Text 2", "Text 3"]
    results = processor.process_batch(texts)
    
    # Performance monitoring
    print(f"Performance Report: {processor.get_performance_report()}")