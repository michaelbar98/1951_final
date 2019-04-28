SELECT *
FROM
(SELECT revenue_now, budget_now, G.genreID
FROM movies
JOIN movie_genre as G
ON movies.id = G.movieID
ORDER BY original_title) as T
WHERE T.revenue_now > 0 and T.budget_now > 0;
