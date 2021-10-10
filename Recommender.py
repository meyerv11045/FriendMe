import implicit
import numpy as np
import scipy
from scipy.sparse import csr_matrix

class Recommender():
    def __init__(self, num_users, num_items):
        self.matrix = csr_matrix((num_items, num_users), dtype=np.float32)

        self.num_users = num_users
        self.num_items = num_items

        model_factors = 2#round(min(num_items, num_users) ** 0.5)
        self.model = implicit.als.AlternatingLeastSquares()#factors = model_factors)s
        #self.model = implicit.approximate_als.NMSLibAlternatingLeastSquares()

    def change_model_factors(self, new_factors):
        self.model = implicit.als.AlternatingLeastSquares(factors = new_factors)
        self.fit()

    def add_new_item(self):
        self.matrix._shape = (self.num_items + 1,self.num_users)

        self.matrix.indptr = np.hstack((self.matrix.indptr,self.matrix.indptr[-1]))        
        self.num_items += 1

        self.fit()

    def add_new_user(self):
        self.matrix = scipy.sparse.hstack((self.matrix,np.zeros(self.num_items,dtype=np.float32)[:,None]))
        self.num_users += 1

        self.fit()


    def fit(self):
        self.model.fit(self.matrix)

    def recommend(self, user_id, number_output):
        if user_id >= self.num_users:
            return None

        user_items = self.matrix.T.tocsr()
        recommendations = self.model.recommend(user_id, user_items, N = number_output, filter_already_liked_items = True)
        
        return recommendations

    def print_matrix(self):
        print(self.matrix.toarray())
    
    def edit_matrix(self, user_list, item_list, score_list):
        assert(len(user_list) == len(item_list) and len(item_list) == len(score_list))

        lil_matrix = self.matrix.tolil()
        
        for i in range(len(user_list)):
            assert(item_list[i] < self.num_items and user_list[i] < self.num_users)
            lil_matrix[item_list[i], user_list[i]] = score_list[i]

        self.matrix = lil_matrix.tocsr()



num_users = 3
num_items = 3

recommender = Recommender(num_users, num_items)

recommender.edit_matrix([0,0,1,2,2,0],[0,1,0,0,1,2],[1,1,1,1,-1,1])

recommender.print_matrix()

recommender.fit()

recommendations = recommender.recommend(1, 10)

print(recommendations)
# for i in range(6):
#     print('User:' + str(i))d
#     recommendations = recommender.recommend(i, 1)

#     print(recommendations)