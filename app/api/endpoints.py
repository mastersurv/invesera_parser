from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from dependency_injector.wiring import inject, Provide

from app.schemas import ParseRequest, SummaryResponse, ArticleResponse
from app.services.article_service import ArticleService
from app.containers import Container

router = APIRouter(prefix="/api/v1", tags=["articles"])


@router.post("/parse", response_model=ArticleResponse)
@inject
async def parse_article(
    request: ParseRequest,
    background_tasks: BackgroundTasks,
    article_service: Annotated[ArticleService, Depends(Provide[Container.article_service])]
):
    """
    Запуск парсинга статьи Википедии с рекурсивным парсингом связанных статей.
    """
    try:
        article = await article_service.parse_and_save_article(str(request.url))
        
        if not article:
            raise HTTPException(status_code=404, detail="Не удалось спарсить статью")
        
        return ArticleResponse.model_validate(article)
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@router.get("/summary", response_model=SummaryResponse)
@inject
async def get_article_summary(
    url: str,
    article_service: ArticleService = Depends(Provide[Container.article_service])
):
    """
    Получение краткого содержания статьи по её URL.
    """
    try:
        summary = await article_service.get_article_summary(url)
        
        if not summary:
            raise HTTPException(status_code=404, detail="Статья не найдена в базе данных")
        
        return summary
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}")


@router.post("/generate-summaries")
@inject
async def generate_pending_summaries(
    background_tasks: BackgroundTasks,
    article_service: ArticleService = Depends(Provide[Container.article_service])
):
    """
    Генерация краткого содержания для всех статей, у которых его ещё нет.
    """
    try:
        background_tasks.add_task(article_service.generate_pending_summaries)
        return {"message": "Генерация краткого содержания запущена в фоновом режиме"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Внутренняя ошибка сервера: {str(e)}") 