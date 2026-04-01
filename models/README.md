# PointMeistro Models Directory

Place trained PointNet++ models here.

## Model Files

- `concrete_steel_segmentation.pth` - Production model (not included, train your own)
- Training data generation scripts in `/python-segmenter/training/`

## Training Your Own Model

1. Export your Tekla model library to IFC
2. Generate synthetic point clouds with `generate_training_data.py`
3. Train PointNet++ with `train.py`
4. Place trained model here as `concrete_steel_segmentation.pth`
5. Restart segmenter: `docker compose restart segmenter`

## Model Architecture

- **Input**: Raw point cloud (N x 3 xyz coordinates)
- **Output**: Per-point classification (N x 5 class probabilities)
- **Classes**: 0=concrete, 1=steel, 2=rebar, 3=formwork, 4=other
- **Expected accuracy**: 95%+ after training on your Tekla library

**Note**: Trained models are large files (100MB+) and should not be committed to Git. Add them to `.gitignore`.
