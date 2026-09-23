from app.schemas import ComicOutline, PanelOutline, ComicStory, PanelStory
from app.services.layout_builder import build_comic_layout

def test_layout_builder():
    outline = ComicOutline(panels=[
        PanelOutline(panel_number=1, title="Start", scene_description="Forest", image_prompt="fox"),
        PanelOutline(panel_number=2, title="Next", scene_description="River", image_prompt="fox river"),
    ])
    story = ComicStory(panels=[
        PanelStory(panel_number=1, caption="Dawn", narration="The fox walks.", dialogue="Hello."),
        PanelStory(panel_number=2, caption="Splash", narration="The fox crosses.", dialogue="Whoa!"),
    ])
    paths = ["/tmp/one.png", "/tmp/two.png"]
    result = build_comic_layout(outline, story, paths)
    assert len(result) == 2
    assert result[0].image_url.endswith("/one.png")
