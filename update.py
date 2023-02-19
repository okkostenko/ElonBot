from get_data import get_data
from fineTune import main
from sklearn.model_selection import train_test_split

def update():
    df=get_data()
    trn_df, val_df=train_test_split(df, test_size=0.1)
    main(trn_df, val_df)

if __name__=='__main__':
    update()