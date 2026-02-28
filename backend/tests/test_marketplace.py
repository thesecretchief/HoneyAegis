"""Tests for the plugin marketplace API."""

from app.api.marketplace import (
    MarketplacePlugin,
    PluginSubmission,
    _REGISTRY,
)


class TestMarketplaceSchemas:
    """Test marketplace API Pydantic schemas."""

    def test_marketplace_plugin(self):
        plugin = MarketplacePlugin(
            plugin_id="test-plugin",
            name="Test Plugin",
            version="1.0.0",
            author="Test Author",
            description="A test plugin",
            plugin_type="hook",
            downloads=100,
            rating=4.5,
            tags=["test", "example"],
            created_at="2026-02-28T00:00:00Z",
            updated_at="2026-02-28T00:00:00Z",
        )
        assert plugin.plugin_id == "test-plugin"
        assert plugin.rating == 4.5
        assert plugin.repo_url is None
        assert plugin.icon_url is None

    def test_marketplace_plugin_with_urls(self):
        plugin = MarketplacePlugin(
            plugin_id="full-plugin",
            name="Full Plugin",
            version="2.0.0",
            author="Author",
            description="Full featured",
            plugin_type="enricher",
            downloads=500,
            rating=4.8,
            tags=["enrichment"],
            repo_url="https://github.com/example/plugin",
            icon_url="https://example.com/icon.png",
            created_at="2026-01-01T00:00:00Z",
            updated_at="2026-02-01T00:00:00Z",
        )
        assert plugin.repo_url == "https://github.com/example/plugin"
        assert plugin.icon_url == "https://example.com/icon.png"

    def test_plugin_submission(self):
        sub = PluginSubmission(
            name="My Plugin",
            version="0.1.0",
            description="Does things",
            plugin_type="hook",
            repo_url="https://github.com/user/plugin",
            tags=["custom"],
        )
        assert sub.name == "My Plugin"
        assert sub.repo_url == "https://github.com/user/plugin"
        assert len(sub.tags) == 1

    def test_plugin_submission_defaults(self):
        sub = PluginSubmission(
            name="Minimal",
            version="0.1.0",
            description="Minimal plugin",
            plugin_type="emulator",
            repo_url="https://github.com/user/minimal",
        )
        assert sub.tags == []


class TestMarketplaceRegistry:
    """Test static marketplace registry."""

    def test_registry_has_plugins(self):
        assert len(_REGISTRY) >= 5

    def test_all_plugins_have_required_fields(self):
        for plugin in _REGISTRY:
            assert plugin.plugin_id
            assert plugin.name
            assert plugin.version
            assert plugin.author
            assert plugin.description
            assert plugin.plugin_type
            assert plugin.downloads >= 0
            assert 0 <= plugin.rating <= 5
            assert plugin.created_at
            assert plugin.updated_at

    def test_plugin_types_valid(self):
        valid_types = {"enricher", "hook", "emulator"}
        for plugin in _REGISTRY:
            assert plugin.plugin_type in valid_types, (
                f"Invalid type: {plugin.plugin_type}"
            )

    def test_ip_blocklist_plugin_exists(self):
        plugin = next(
            (p for p in _REGISTRY if p.plugin_id == "ip-blocklist"), None
        )
        assert plugin is not None
        assert plugin.plugin_type == "enricher"

    def test_auto_ip_block_plugin_exists(self):
        plugin = next(
            (p for p in _REGISTRY if p.plugin_id == "auto-ip-block"), None
        )
        assert plugin is not None
        assert plugin.plugin_type == "hook"

    def test_all_plugins_have_tags(self):
        for plugin in _REGISTRY:
            assert len(plugin.tags) >= 1

    def test_ratings_in_valid_range(self):
        for plugin in _REGISTRY:
            assert 0.0 <= plugin.rating <= 5.0
