import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

from sklearn import datasets
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV

#define a pipeline to search for best combo of PCA truncc
#and classifier regulatization

pca = PCA()
#set the tolerance to a large value to make the example faster
logistic = LogisticRegression(max_iter=1000, tol = 0.1)
pipe = Pipeline(steps = [('pca', pca), ('logistic', logistic)])

X_digits, y_digits = datasets.load_digits(return_X_y = True)

#parameters of pipelines can be set using '__' separated parameters
param_grid = {
    'pca__n_components': [5, 15, 30, 45, 64],
    'logistic__C': np.logspace(-4, 4, 4),
}
search = GridSearchCV(pipe, param_grid, n_jobs = -1)
search.fit(X_digits, y_digits)
print("Best parameter (CV score = %0.3f):" % search.best_score_)
print(search.best_params_)

#plot the PCA spectrum
pca.fit(X_digits)

fig, (ax0, ax1) = plt.subplots(nrows = 2, sharex = True, figsize = (6, 6))
ax0.plot(np.arange(1, pca.n_components_ + 1),
         pca.explained_variance_ratio_, '+', linewidth = 2)
ax0.set_ylabel('PCA explained variance ratio')

ax0.axvline(search.best_estimator_.named_steps['pca'].n_components,
            linestyle = ':', label = 'n_components chosen')
ax0.legend(prop = dict(size=12))

plt.show()
