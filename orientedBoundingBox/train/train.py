from ultralytics import YOLO
 
if __name__ == '__main__':
    # Load a model
    model = YOLO('yolo11n-obb.pt')  # load a pretrained model

    # Train the model with custom settings
    model.train(
        data='dataset.yaml',      # path to data config file
        epochs=20,              # number of epochs
        imgsz=1024,             # image size
        batch=16,               # batch size
        optimizer='Adam',
        device='cuda',             # cuda device (use 'cpu' for CPU)
        project='runs/train',   # save results to project/name
        name='exp_yolo11_'+str(epochs)+'_'+str(batch)+'_'+str(optimizer)              # experiment name
    )
