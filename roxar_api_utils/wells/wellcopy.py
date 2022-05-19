import numpy as np

import roxar
import roxar.wells


def copy_well(dst_well, src_well, copy_logs=True):
    """Copy RMS well
    Args:
        dst_well (RMS well): Destination well
        src_well (RMS well): Source well
        copy_logs (bool): copy log runs, True or False
    """
    dst_well.wellhead = src_well.wellhead
    dst_well.rkb = src_well.rkb
    copy_trajectories(dst_well.wellbore, src_well.wellbore, copy_logs=copy_logs)
    copy_wellbores(dst_well.wellbore, src_well.wellbore)

    return None


def copy_wellbores(dst_wellbore, src_wellbore):
    """Copy RMS wellbore
    Args:
        dst_wellbore (RMS wellbore): Destination wellbore
        src_wellbore (RMS wellbore): Source wellbore
    """
    for src_wellbore2 in src_wellbore.wellbores:
        dst_wellbore2 = dst_wellbore.wellbores.create(src_wellbore2.name)
        copy_trajectories(dst_wellbore2, src_wellbore2)
        copy_wellbores(dst_wellbore2, src_wellbore2)

    return None


def copy_log_curves(dst_log_run, src_log_run):
    """Copy RMS log run
    Args:
        dst_log_run (RMS log run): Destination log run
        src_log_run (RMS log run): Source log run
    """
    for src_log_curve in src_log_run.log_curves:
        name = src_log_curve.name
        dst_log_curve = None
        if src_log_curve.is_discrete:
            dst_log_curve = dst_log_run.log_curves.create_discrete(name)
            # special handling when log_curve has no code names
            code_names = src_log_curve.get_code_names()
            if len(code_names) > 0:
                try:
                    dst_log_curve.set_code_names(code_names)
                except ValueError as e:
                    errmes = (
                        "Copy log curves failed: "
                        + src_log_curve.name
                        + " Wellbore: "
                        + src_log_run.trajectory.wellbore.name
                        + " Reason: "
                        + e
                    )
                    raise ValueError(errmes)
        else:
            dst_log_curve = dst_log_run.log_curves.create(name)
        values = src_log_curve.get_values()
        try:
            dst_log_curve.set_values(values)
        except ValueError as e:
            errmes = (
                "Copy log curves failed: "
                + src_log_curve.name
                + " Wellbore: "
                + src_log_run.trajectory.wellbore.name
                + " Reason: "
                + e
            )
        if len(dst_log_curve.get_values()) != len(src_log_curve.get_values()):
            dst_log_curve.set_values(values)

    return None


def copy_log_runs(dst_traj, src_traj):
    """Copy RMS log runs
    Args:
        dst_log_traj (RMS trajectory): Destination trajectory
        src_log_traj (RMS trajectory): Source trajectory
    """
    for src_log_run in src_traj.log_runs:
        name = src_log_run.name
        measured_depths = src_log_run.get_measured_depths()
        dst_log_run = dst_traj.log_runs.create(name)
        try:
            dst_log_run.set_measured_depths(measured_depths)
        except ValueError as e:
            errmes = (
                "Copy log runs failed. Run: "
                + src_log_run.name
                + " Wellbore: "
                + src_log_run.trajectory.wellbore.name
                + " Reason: "
                + e
            )
            raise ValueError(errmes)
        copy_log_curves(dst_log_run, src_log_run)

    return None


def copy_trajectories(
    dst_wellbore, src_wellbore, dst_parent_traj=None, md_min=None, copy_logs=True
):
    """Copy RMS trajectories
    Args:
        dst_wellbore (RMS wellbore): Destination wellbore
        src_wellbore (RMS wellbore): Source log wellbore
        dst_parent_traj (RMS trajectory): Destination parent trajectory
        md_min (float): Optional minimum measured depth
    Note:
        Only survey points euqal to or below the md_min value is copied
        A suvey point corresponding to md_min will be added to the trajectory.
    """
    for src_traj in src_wellbore.trajectories:
        name = src_traj.name
        dst_traj = None
        if dst_parent_traj is None:
            if src_traj.parent_trajectory is None:
                dst_traj = dst_wellbore.trajectories.create(name)
            else:
                dst_parent_traj = None
                if src_wellbore.parent_wellbore is None:
                    print(
                        "Copy trajectory: Parent source wellbore is None. ProjectAhead?",
                        "traj:",
                        src_traj.name,
                        "well:",
                        src_wellbore.name,
                    )
                    continue
                try:
                    dst_parent_wellbore = dst_wellbore.well.all_wellbores[
                        src_wellbore.parent_wellbore.name
                    ]
                    dst_parent_traj = dst_parent_wellbore.trajectories[
                        src_traj.parent_trajectory.name
                    ]
                except KeyError as e:
                    errmes = (
                        "Copy trajectory failed: "
                        + src_traj.name
                        + " Wellbore: "
                        + src_wellbore.name
                    )
                    raise KeyError(errmes)

                dst_traj = dst_wellbore.trajectories.create_sidetrack(
                    name, dst_parent_traj
                )
        else:
            dst_traj = dst_wellbore.trajectories.create_sidetrack(name, dst_parent_traj)

        if copy_logs:
            copy_log_runs(dst_traj, src_traj)

        points = None
        src_type = src_traj.survey_point_series.calculation_type
        if src_type == roxar.SurveyPointCalculationType.survey_points:
            points = src_traj.survey_point_series.get_survey_points()
        elif src_type == roxar.SurveyPointCalculationType.none:
            points = src_traj.survey_point_series.get_survey_points()
        elif src_type == roxar.SurveyPointCalculationType.surveys:
            points = src_traj.survey_point_series.get_surveys()
        elif src_type == roxar.SurveyPointCalculationType.points:
            points = src_traj.survey_point_series.get_points()
        elif src_type == roxar.SurveyPointCalculationType.measured_depths_and_points:
            points = src_traj.survey_point_series.get_measured_depths_and_points()
        else:
            points = src_traj.survey_point_series.get_survey_points()

        # Filter trajectorie above tie-in point:
        if src_type == roxar.SurveyPointCalculationType.survey_points:  # 6 arguments
            nlist = []
            if md_min is not None:
                is_first = True
                for p in points:
                    if p[0] == md_min:
                        nlist.append(p)
                        is_first = False
                    elif p[0] > md_min:
                        if is_first:
                            pfirst = (
                                src_traj.survey_point_series.interpolate_survey_point(
                                    md_min
                                )
                            )
                            nlist.append(pfirst)
                            is_first = False
                        nlist.append(p)
                points = np.array(nlist)
        elif src_type == roxar.SurveyPointCalculationType.surveys:  # 3 arguments
            nlist = []
            if md_min is not None:
                is_first = True
                for p in points:
                    if p[0] == md_min:
                        nlist.append(p)
                        is_first = False
                    elif p[0] > md_min:
                        if is_first:
                            pfirst = (
                                src_traj.survey_point_series.interpolate_survey_point(
                                    md_min
                                )
                            )
                            p0 = np.array([pfirst[0], pfirst[1], pfirst[2]])
                            nlist.append(p0)
                            is_first = False
                        nlist.append(p)
                points = np.array(nlist)
        elif src_type == roxar.SurveyPointCalculationType.measured_depths_and_points:
            spoints = src_traj.survey_point_series.get_survey_points()
            nlist = []
            if md_min is not None:
                is_first = True
                for i, sp in enumerate(spoints):
                    if sp[0] == md_min:
                        nlist.append(points[i])
                        is_first = False
                    elif sp[0] > md_min:
                        if is_first:
                            pfirst = (
                                src_traj.survey_point_series.interpolate_survey_point(
                                    md_min
                                )
                            )
                            p0 = np.array([pfirst[0], pfirst[3], pfirst[4], pfirst[5]])
                            nlist.append(p0)
                            is_first = False
                        nlist.append(points[i])
                points = np.array(nlist)
        elif src_type == roxar.SurveyPointCalculationType.points:
            spoints = src_traj.survey_point_series.get_survey_points()
            nlist = []
            if md_min is not None:
                is_first = True
                for i, sp in enumerate(spoints):
                    if sp[0] == md_min:
                        nlist.append(points[i])
                        is_first = False
                    elif sp[0] > md_min:
                        if is_first:
                            pfirst = (
                                src_traj.survey_point_series.interpolate_survey_point(
                                    md_min
                                )
                            )
                            p0 = np.array([pfirst[3], pfirst[4], pfirst[5]])
                            nlist.append(p0)
                            is_first = False
                        nlist.append(points[i])
                points = np.array(nlist)

        if len(points) == 0:
            print(
                "Copy_trajectories: Trajectory has no survey points:",
                src_traj.name,
                "Wellbore:",
                src_traj.wellbore.name,
            )
            continue
        if src_type == roxar.SurveyPointCalculationType.survey_points:
            try:
                dst_traj.survey_point_series.set_survey_points(points)
            except ValueError as e:
                raise ValueError(e)
        elif src_type == roxar.SurveyPointCalculationType.none:
            try:
                dst_traj.survey_point_series.set_survey_points(points)
            except ValueError as e:
                raise ValueError(e)
        elif src_type == roxar.SurveyPointCalculationType.surveys:
            try:
                dst_traj.survey_point_series.set_surveys(points)
            except ValueError as e:
                raise ValueError(e)
        elif src_type == roxar.SurveyPointCalculationType.points:
            try:
                dst_traj.survey_point_series.set_points(points)
            except ValueError as e:
                raise ValueError(e)
        elif src_type == roxar.SurveyPointCalculationType.measured_depths_and_points:
            try:
                dst_traj.survey_point_series.set_measured_depths_and_points(points)
            except ValueError as e:
                raise ValueError(e)
        else:
            try:
                dst_traj.survey_point_series.set_survey_points(points)
            except ValueError as e:
                raise ValueError(e)

        dst_traj.survey_point_series.interpolation_type = (
            src_traj.survey_point_series.interpolation_type
        )

    return None
