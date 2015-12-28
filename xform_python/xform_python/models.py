# ----------------------------------------------------------------------------
# File:    models.py
# Author:  Michael Gharbi <gharbi@mit.edu>
# Created: 2015-02-11
# ----------------------------------------------------------------------------
#
# Parameters and Result models
#
# ---------------------------------------------------------------------------#


import os
import shutil
import ConfigParser

def str2bool(s):
    return s.lower() in ["True", "true", "1", "y", "yes"]

class Result():
    """ Holds the results for an input/output pair.

    Attributes:
        name (CharField): name of the image pair
        category (ForeignKey): filter category of the image pair
        experiment (ForeignKey): experiment the result belongs to
        outputPath (CharField): path to the data generated by the program
        inputPath (CharField): path to input/output images pair
        psnr (FloatField): error of reconstruciont w.r.t. to the groundtruth
        ssim (FloatField): error of reconstruciont w.r.t. to the groundtruth
        computation_time (FloatField): end-to-end computation time
        compression_up (FloatField): uploaded data ratio vs. uncrompressed image
        compression_down (FloatField): downloaded data ratio vs. uncrompressed image
        error (CharField): any error that might happen while processing

    """
    # Identification
    def __init__(self):
        # File access
        self.dataPath   = ""
        self.outputPath = ""
        
        # Evaluation
        self.psnr             = 0
        self.ssim             = 0
        self.computation_time = 0
        self.compression_up   = 0
        self.compression_down = 0
        self.max_error_x      = 0
        self.max_error_y      = 0

    def unprocessedPath(self):
        """Path to the unprocessed image"""

        return os.path.join(self.dataPath, "unprocessed.png")

    def processedPath(self):
        """Path to the processed image"""

        return os.path.join(self.dataPath, "processed.png")

    def reconstructedPath(self):
        """Path to our reconstruction"""

        return os.path.join(self.outputPath, "reconstructed.jpg")

class Parameters():
    """ Parameters of the algorithm associated to a given experiment.

    Args:
        experiment (OneToOneField): experiment these parameters belong to
        transform_model (CharField): transform model used (e.g jpeg, recipe...)
        pipeline (CharField): array of pipeline node in JSON format
        epsilon (FloatField): regularization parameter for the optimization
        wSize (IntegerField): size of the window for recipe fitting
        use_patch_overlap (BooleanField): overlap patches by half a patch
        use_multiscale_feat (BooleanField): laplacian pyramid features
        use_tonecurve_feat (BooleanField): non-linear luminance mapping
        in_downsampling (IntegerField): downsampling ratio for the input
        in_quality (IntegerField): compression quality of the input
        recipe_format (CharField): image file format to save the recipe

    """
    def __init__(self):

    # Pipeline description
        self.transform_model        = "RecipeModel"
        self.pipeline               = '["ImageInitializer","JPEGinputCompressor","RGB2YCbCr", "ModelBuilder","UniformEncoder", "RecipeImageCompressor", "UniformDecoder", "Reconstructor", "YCbCr2RGB", "ClampToUint8", "ImageExporter"]'

        # Input file parameters
        self.in_downsampling        = 4
        self.in_quality             = 75
        self.add_noise              = True

        # Recipe parameters
        self.epsilon                = 1e-3
        self.wSize                  = 64
        self.use_patch_overlap      = True
        self.use_multiscale_feat    = True
        self.use_tonecurve_feat     = True
        self.luma_bands             = 6
        self.ms_levels              = -1
        self.recipe_format          = ".png"
        self.transfer_multiscale    = True

    def load(self,path):
        """ Load parameters from .cfg file"""
        cp             = ConfigParser.ConfigParser()
        cp.optionxform = str
        cp.read(path)
        d = dict(cp._sections)
        for key in d:
            d[key] = dict(**d[key])
            d[key].pop('__name__',None)
        self.update(d)

    def update(self,params):
        for key in params:
            if key == "Pipeline":
                for k in params[key]:
                    if hasattr(self,k):
                        self.__setattr__(k,params[key][k])
            if key == "List":
                for k in params[key]:
                    if hasattr(self,k):
                        self.__setattr__(k,params[key][k])
            elif key == "Int":
                for k in params[key]:
                    if hasattr(self,k):
                        self.__setattr__(k,int(params[key][k]))
            elif key == "Float":
                for k in params[key]:
                    if hasattr(self,k):
                        self.__setattr__(k,float(params[key][k]))
            elif key == "Bool":
                for k in params[key]:
                    if hasattr(self,k):
                        self.__setattr__(k,str2bool(params[key][k]))
            elif key == "String":
                for k in params[key]:
                    if hasattr(self,k):
                        self.__setattr__(k,params[key][k])
        self.save()

    def __unicode__(self):
        return "%s - params" % self.experiment.__unicode__()

    class Meta:
        verbose_name_plural = "parameters"
