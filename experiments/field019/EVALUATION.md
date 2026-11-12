# Cross-domain inference, calibration, and falsification

**Generative claim:** having the drawing, multiple pictures, and one approximate known height constrains one coherent but uncertain 3-D scene. Photos are not inherently calibrated camera frames; a camera is a model with intrinsic parameters and extrinsic pose (both latent unless known). One height anchors scale only when the vertical object is correctly identified and geometrically related to the model.

**Source slots:** source sketch coordinate frame (arbitrary normalized units), each photo pixel frame, three-dimensional world frame (meters, Y down, local arbitrary origin), reference height (user approx), candidate calibration and camera pose, uncertainty and contradictions.

**Model identifiability:** two independent views with at least five noncollinear shared base/top post landmarks and separately supplied pinhole intrinsics; not sufficient if the views are near identical, feature correspondence is wrong, significant distortion occurs or physical tops/bases are obscured. We do not permit fitted intrinsics to stand in for measured ones without a separate uncertainty study.

**Scoring:** reprojection RMS, scale sensitivity vs ±30% scale alternatives, soft sketch correction magnitude as fraction of sketch extent, outlier residuals, source provenance; hold on contradiction, missing independent input or broad scale ambiguity. Fits are not structural or safety certificates.

**Critical remaining real tasks:** (1) independently identify the same fixed fence posts or corners in overlapping photos, (2) distinguish near 6-foot fences from smaller cage panels and taller gates, (3) establish camera intrinsics or explicit priors, (4) quantify how unscaled and not-to-scale the drawing is, and (5) physically measure one horizontal dimension to independently validate inference. Pixel overlays and explicit human correction in shared board can supply these without lengthy textual explanation.

**Honest result:** no reliable shared cross-photo 3-D landmarks or lens intrinsics have yet been obtained from the real user's images. Real yard dimensions and camera poses remain unknown. Synthetic numerical inversion is the only metric reconstruction demonstrated.
