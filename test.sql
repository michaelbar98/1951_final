SELECT *
FROM
(SELECT original_title, revenue_now, budget_now, Y.views, Y.likes, Y.dislikes
FROM movies 
JOIN youtube_clean as Y
ON movies.original_title = Y.name
ORDER BY original_title) as T
WHERE T.revenue_now > 0;
