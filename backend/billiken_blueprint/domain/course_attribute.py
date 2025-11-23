from dataclasses import dataclass


@dataclass
class CourseAttribute:
    name: str
    degree_works_label: str
    courses_slu_label: str


class CourseAttributes:
    UIS = CourseAttribute("Ignite Seminar", "UIS", "uuc_attr_UIS")
    UUQP = CourseAttribute("Ultimate Questions: Philosophy", "UUQP", "uuc_attr_UUQP")
    UUQT = CourseAttribute("Ultimate Questions: Theology", "UUQT", "uuc_attr_UUQT")
    UCI = CourseAttribute("Collaborative Inquiry", "UCI", "uuc_attr_UCI")
    USCM = CourseAttribute("Self in Community", "USCM", "uuc_attr_USCM")
    USCN = CourseAttribute("Self in Contemplation", "USCN", "uscn")
    USW = CourseAttribute("Self in the World", "USW", "uuc_attr_USW")
    UAHC = CourseAttribute("Aesthetics, History and Culture", "UAHC", "uuc_attr_UAHC")
    UNAS = CourseAttribute("Natural and Applied Sciences", "UNAS", "uuc_attr_UNAS")
    UQR = CourseAttribute("Quantitative Reasoning", "UQR", "uuc_attr_UQR")
    USBD = CourseAttribute("Social and Behavioral Sciences", "USBD", "uuc_attr_USBS")
    UWVC = CourseAttribute("Written & Visual Communication", "UWVC", "uuc_attr_UWVC")
    UOVC = CourseAttribute("Oral & Visual Communication", "UOVC", "uuc_attr_UOVC")
    UCE = CourseAttribute("Creative Expression", "UCE", "uuc_attr_UCE")
    UWI = CourseAttribute("Writing Intensive", "UWI", "writing_intensive")
    UIIC = CourseAttribute("Identities in Context", "UIIC", "identities_in_context")
    UGI = CourseAttribute("Global Interdependence", "UGI", "global_interdependence")
    UDEJ = CourseAttribute(
        "Diversity, Ethics, and a Just Society", "UDEJ", "just_society"
    )
    URIA = CourseAttribute("Reflection-in-Action", "URIA", "reflection_in_action")
