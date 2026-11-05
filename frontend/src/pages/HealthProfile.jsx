import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

import {
  Activity,
  HeartPulse,
  UserRound,
  Ruler,
  Weight,
  Target,
  Save,
  CheckCircle2,
  UploadCloud,
  FileText,
  Trash2,
  RefreshCw,
  X,
} from "lucide-react";

import api from "../services/api";


function HealthProfile() {
  const navigate = useNavigate();

  const { user: authUser } = useAuth();
  const USER_ID = authUser.id;


  const [formData, setFormData] = useState({
    name: "",
    age: "",
    gender: "",
    height_cm: "",
    weight_kg: "",

    systolic_bp: "",
    diastolic_bp: "",
    blood_sugar_mg_dl: "",
    thyroid_status: "",

    activity_level: "",
    diet_preference: "",
    food_region: "",
    goal: "",

    women_health_condition: "",

    additional_health_info: [],
  });


  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  const [profileExists, setProfileExists] =
    useState(false);

  const [error, setError] = useState("");

  const [successMessage, setSuccessMessage] =
    useState("");

  // =========================================================
  // HEALTH REPORT STATE
  // =========================================================

  const [reportFile, setReportFile] = useState(null);
  const [reportInputKey, setReportInputKey] = useState(0);
  const [analyzingReport, setAnalyzingReport] = useState(false);
  const [confirmingReport, setConfirmingReport] = useState(false);
  const [reportPreview, setReportPreview] = useState(null);
  const [reportDraft, setReportDraft] = useState(null);
  const [reportHistory, setReportHistory] = useState([]);
  const [reportHistoryLoading, setReportHistoryLoading] = useState(false);
  const [deletingReportId, setDeletingReportId] = useState(null);
  const [reportMessage, setReportMessage] = useState("");
  const [reportError, setReportError] = useState("");


  useEffect(() => {
    loadProfile();
  }, []);


  // =========================================================
  // LOAD PROFILE
  // =========================================================

  async function loadProfile() {
    try {
      setLoading(true);
      setError("");

      const response = await api.get(
        `/users/${USER_ID}/profile`
      );

      const data = response.data;

      const user =
        data.user || data;

      const health =
        data.health_profile ||
        data.health ||
        {};

      const hasHealthProfile =
        Boolean(
          data.health_profile ||
          data.health
        );

      setProfileExists(
        hasHealthProfile
      );


      setFormData({
        name:
          user.name ?? "",

        age:
          user.age ?? "",

        gender:
          user.gender ?? "",

        height_cm:
          user.height_cm ?? "",

        weight_kg:
          user.weight_kg ?? "",


        systolic_bp:
          health.systolic_bp ?? "",

        diastolic_bp:
          health.diastolic_bp ?? "",

        blood_sugar_mg_dl:
          health.blood_sugar_mg_dl ?? "",

        thyroid_status:
          health.thyroid_status ?? "",


        activity_level:
          health.activity_level ?? "",

        diet_preference:
          health.diet_preference ?? "",

        food_region:
          health.food_region ?? "",

        goal:
          health.goal ?? "",


        women_health_condition:
          health.women_health_condition ??
          (
              user.gender
              ?.toLowerCase()
              .trim() === "female"
              ? "none"
              : ""
          ),

        additional_health_info:
          Array.isArray(health.additional_health_info)
          ? health.additional_health_info
          : [],
      });

      if (hasHealthProfile) {
        await loadReportHistory();
      }

    } catch (err) {
      console.error(
        "Profile loading error:",
        err
      );

      setError(
        err.response?.data?.detail ||
          "Could not load your health profile."
      );

    } finally {
      setLoading(false);
    }
  }


  // =========================================================
  // HANDLE FORM CHANGES
  // =========================================================

  function handleChange(event) {
    const {
      name,
      value,
    } = event.target;


    setFormData((previous) => {
      const updated = {
        ...previous,
        [name]: value,
      };


      /*
       * Women's health information is only used
       * when Female is selected.
       *
       * If the user changes gender away from Female,
       * remove the previous women's-health selection.
       */

      if (
        name === "gender" &&
        value.toLowerCase() !== "female"
      ) {
        updated.women_health_condition = "";
      }


      /*
       * When Female is selected for the first time,
       * default the field to "none".
       */

      if (
        name === "gender" &&
        value.toLowerCase() === "female" &&
        !previous.women_health_condition
      ) {
        updated.women_health_condition = "none";
      }


      return updated;
    });


    setSuccessMessage("");
  }


  // =========================================================
  // SAVE PROFILE
  // =========================================================

  async function handleSubmit(event) {
    event.preventDefault();


    try {
      setSaving(true);
      setError("");
      setSuccessMessage("");


      const isFemale =
        formData.gender
          .toLowerCase()
          .trim() === "female";


      // =====================================================
      // EXISTING PROFILE
      // =====================================================

      if (profileExists) {
        const updatePayload = {
        

          height_cm:
            Number(
              formData.height_cm
            ),

          weight_kg:
            Number(
              formData.weight_kg
            ),


          systolic_bp:
            formData.systolic_bp
              ? Number(
                  formData.systolic_bp
                )
              : null,

          diastolic_bp:
            formData.diastolic_bp
              ? Number(
                  formData.diastolic_bp
                )
              : null,

          blood_sugar_mg_dl:
            formData.blood_sugar_mg_dl
              ? Number(
                  formData.blood_sugar_mg_dl
                )
              : null,

          thyroid_status:
            formData.thyroid_status ||
            null,


          activity_level:
            formData.activity_level,

          diet_preference:
            formData.diet_preference ||
            null,

          additional_health_info:
            Array.isArray(formData.additional_health_info)
              ? formData.additional_health_info
              : [],

          food_region:
            formData.food_region ||
            null,

          goal:
            formData.goal,


          women_health_condition:
            isFemale
              ? (
                  formData.women_health_condition ||
                  "none"
                )
              : null,
        };


        const response =
          await api.put(
            `/users/${USER_ID}/profile`,
            updatePayload
          );


        const data =
          response.data;

        const user =
          data.user;

        const health =
          data.health_profile;


        setFormData({
          name:
            user.name ?? "",

          age:
            user.age ?? "",

          gender:
            user.gender ?? "",

          height_cm:
            user.height_cm ?? "",

          weight_kg:
            user.weight_kg ?? "",


          systolic_bp:
            health.systolic_bp ?? "",

          diastolic_bp:
            health.diastolic_bp ?? "",

          blood_sugar_mg_dl:
            health.blood_sugar_mg_dl ?? "",

          thyroid_status:
            health.thyroid_status ?? "",


          activity_level:
            health.activity_level ?? "",

          diet_preference:
            health.diet_preference ?? "",

          food_region:
            health.food_region ?? "",

          goal:
            health.goal ?? "",


          women_health_condition:
            health.women_health_condition ??
            (
              user.gender
                ?.toLowerCase()
                .trim() === "female"
                ? "none"
                : ""
            ),

            additional_health_info:
              Array.isArray(
                health.additional_health_info
          )
            ? health.additional_health_info
            : [],
        });


        setSuccessMessage(
          "Health profile updated successfully."
        );
      }


      // =====================================================
      // NEW PROFILE
      // =====================================================

      else {
        const createPayload = {
          user_id:
            USER_ID,


          systolic_bp:
            formData.systolic_bp
              ? Number(
                  formData.systolic_bp
                )
              : null,

          diastolic_bp:
            formData.diastolic_bp
              ? Number(
                  formData.diastolic_bp
                )
              : null,

          blood_sugar_mg_dl:
            formData.blood_sugar_mg_dl
              ? Number(
                  formData.blood_sugar_mg_dl
                )
              : null,

          thyroid_status:
            formData.thyroid_status ||
            null,


          activity_level:
            formData.activity_level,

          diet_preference:
            formData.diet_preference ||
            null,

          additional_health_info:
            Array.isArray(formData.additional_health_info)
              ? formData.additional_health_info
              : [],

          food_region:
            formData.food_region ||
            null,

          goal:
            formData.goal,


          women_health_condition:
            isFemale
              ? (
                  formData.women_health_condition ||
                  "none"
                )
              : null,
        };


        await api.post(
          "/health-profile",
          createPayload
        );


        setProfileExists(true);


        /*
         * First-time onboarding is complete.
         * Send the new user to Dashboard.
         */

        navigate("/");
      }

    } catch (err) {
      console.error(
        "Profile save error:",
        err
      );


      setError(
        err.response?.data?.detail ||
          "Could not save your health profile."
      );

    } finally {
      setSaving(false);
    }
  }


  // =========================================================
  // HEALTH REPORTS
  // =========================================================

  async function loadReportHistory() {
    try {
      setReportHistoryLoading(true);

      const response = await api.get(
        "/health-reports"
      );

      setReportHistory(
        Array.isArray(response.data?.reports)
          ? response.data.reports
          : []
      );

    } catch (err) {
      console.error(
        "Health report history error:",
        err
      );

    } finally {
      setReportHistoryLoading(false);
    }
  }


  function handleReportFileChange(event) {
    const file =
      event.target.files?.[0] || null;

    setReportError("");
    setReportMessage("");
    setReportPreview(null);
    setReportDraft(null);

    if (!file) {
      setReportFile(null);
      return;
    }

    const allowedTypes = [
      "application/pdf",
      "image/jpeg",
      "image/jpg",
      "image/png",
      "image/webp",
    ];

    if (!allowedTypes.includes(file.type)) {
      setReportFile(null);
      setReportError(
        "Upload a PDF, JPG, JPEG, PNG or WEBP health report."
      );
      setReportInputKey((value) => value + 1);
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      setReportFile(null);
      setReportError(
        "Health report must be 10 MB or smaller."
      );
      setReportInputKey((value) => value + 1);
      return;
    }

    setReportFile(file);
  }


  function clearSelectedReport() {
    setReportFile(null);
    setReportPreview(null);
    setReportDraft(null);
    setReportError("");
    setReportMessage("");
    setReportInputKey((value) => value + 1);
  }


  async function handleAnalyzeReport() {
    if (!profileExists) {
      setReportError(
        "Complete and save your health profile before uploading a health report."
      );
      return;
    }

    if (!reportFile) {
      setReportError(
        "Select a health report first."
      );
      return;
    }

    try {
      setAnalyzingReport(true);
      setReportError("");
      setReportMessage("");

      const data = new FormData();
      data.append("report", reportFile);

      const response = await api.post(
        "/health-report/analyze",
        data,
        {
          headers: {
            "Content-Type": "multipart/form-data",
          },
          timeout: 180000,
        }
      );

      const preview = response.data;
      const extracted = preview?.extracted || {};

      setReportPreview(preview);

      setReportDraft({
        original_filename:
          preview?.original_filename ||
          reportFile.name,

        report_date:
          preview?.report_date || "",

        systolic_bp:
          extracted.systolic_bp ?? "",

        diastolic_bp:
          extracted.diastolic_bp ?? "",

        blood_sugar_mg_dl:
          extracted.blood_sugar_mg_dl ?? "",

        thyroid_status:
          extracted.thyroid_status ?? "",

        additional_health_info:
          Array.isArray(
            extracted.additional_health_info
          )
            ? extracted.additional_health_info.map(
                (item) => ({
                  name: item?.name ?? "",
                  value: item?.value ?? "",
                  unit: item?.unit ?? "",
                  report_flag:
                    item?.report_flag ?? "",
                })
              )
            : [],
      });

      setReportMessage(
        "Report analyzed. Review the extracted values before confirming."
      );

    } catch (err) {
      console.error(
        "Health report analysis error:",
        err
      );

      setReportError(
        err.response?.data?.detail ||
          "Could not analyze the health report."
      );

    } finally {
      setAnalyzingReport(false);
    }
  }


  function updateReportDraftField(
    field,
    value
  ) {
    setReportDraft((previous) => ({
      ...previous,
      [field]: value,
    }));
  }


  function updateAdditionalHealthItem(
    index,
    field,
    value
  ) {
    setReportDraft((previous) => {
      const items = [
        ...(previous?.additional_health_info || []),
      ];

      items[index] = {
        ...items[index],
        [field]: value,
      };

      return {
        ...previous,
        additional_health_info: items,
      };
    });
  }


  function removeAdditionalHealthItem(index) {
    setReportDraft((previous) => ({
      ...previous,
      additional_health_info:
        (
          previous?.additional_health_info ||
          []
        ).filter(
          (_, itemIndex) =>
            itemIndex !== index
        ),
    }));
  }


  function addAdditionalHealthItem() {
    setReportDraft((previous) => ({
      ...previous,
      additional_health_info: [
        ...(
          previous?.additional_health_info ||
          []
        ),
        {
          name: "",
          value: "",
          unit: "",
          report_flag: "",
        },
      ],
    }));
  }


  async function handleConfirmReport() {
    if (!reportDraft) {
      return;
    }

    try {
      setConfirmingReport(true);
      setReportError("");
      setReportMessage("");

      const cleanAdditional =
        (
          reportDraft.additional_health_info ||
          []
        )
          .filter(
            (item) =>
              item.name?.trim()
          )
          .map((item) => ({
            name: item.name.trim(),
            value:
              item.value?.trim() || null,
            unit:
              item.unit?.trim() || null,
            report_flag:
              item.report_flag?.trim() || null,
          }));

      const payload = {
        original_filename:
          reportDraft.original_filename,

        report_date:
          reportDraft.report_date || null,

        systolic_bp:
          reportDraft.systolic_bp !== ""
            ? Number(reportDraft.systolic_bp)
            : null,

        diastolic_bp:
          reportDraft.diastolic_bp !== ""
            ? Number(reportDraft.diastolic_bp)
            : null,

        blood_sugar_mg_dl:
          reportDraft.blood_sugar_mg_dl !== ""
            ? Number(
                reportDraft.blood_sugar_mg_dl
              )
            : null,

        thyroid_status:
          reportDraft.thyroid_status?.trim() ||
          null,

        additional_health_info:
          cleanAdditional,
      };

      await api.post(
        "/health-report/confirm",
        payload
      );

      await loadProfile();

      setReportMessage(
        "Health report confirmed and your active health profile was updated."
      );

      setReportFile(null);
      setReportPreview(null);
      setReportDraft(null);
      setReportInputKey((value) => value + 1);

    } catch (err) {
      console.error(
        "Health report confirmation error:",
        err
      );

      setReportError(
        err.response?.data?.detail ||
          "Could not confirm the health report."
      );

    } finally {
      setConfirmingReport(false);
    }
  }


  async function handleDeleteReport(reportId) {
    const shouldDelete = window.confirm(
      "Delete this report history record? Your current confirmed health-profile values will remain unchanged."
    );

    if (!shouldDelete) {
      return;
    }

    try {
      setDeletingReportId(reportId);
      setReportError("");
      setReportMessage("");

      await api.delete(
        `/health-reports/${reportId}`
      );

      await loadReportHistory();

      setReportMessage(
        "Report history record deleted. Your active health profile was not changed."
      );

    } catch (err) {
      console.error(
        "Health report deletion error:",
        err
      );

      setReportError(
        err.response?.data?.detail ||
          "Could not delete the health report."
      );

    } finally {
      setDeletingReportId(null);
    }
  }


  // =========================================================
  // BMI PREVIEW
  // =========================================================

  const height =
    Number(
      formData.height_cm
    );

  const weight =
    Number(
      formData.weight_kg
    );


  const bmi =
    height > 0 &&
    weight > 0

      ? (
          weight /
          Math.pow(
            height / 100,
            2
          )
        ).toFixed(1)

      : "--";


  const isFemale =
    formData.gender
      .toLowerCase()
      .trim() === "female";


  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return (
      <div className="page-state">

        <div className="loading-spinner">
        </div>

        <h2>
          Loading your profile
        </h2>

        <p>
          Getting your health information
          from MealMind.
        </p>

      </div>
    );
  }


  // =========================================================
  // PAGE
  // =========================================================

  return (
    <div className="health-page">


      {/* API Error */}

      {error && (
        <div className="message-box error-message">
          {error}
        </div>
      )}


      {/* Success Message */}

      {successMessage && (
        <div className="message-box success-message">

          <CheckCircle2 size={18} />

          {successMessage}

        </div>
      )}


      {/* Page Heading */}

      <section className="health-header">

        <div>

          <p className="eyebrow">
            PERSONAL HEALTH PROFILE
          </p>

          <h1>
            Your Health Details
          </h1>

          <p>
            Keep your information up to date
            so MealMind can personalize your
            diet plan and meal recommendations.
          </p>

        </div>


        <div className="profile-status">

          <CheckCircle2 size={18} />

          {profileExists
            ? "Profile Complete"
            : "Profile Setup Required"}

        </div>

      </section>


      {/* Summary */}

      <section className="health-summary">

        <SummaryCard
          icon={
            <Ruler size={20} />
          }
          label="Height"
          value={
            formData.height_cm
              ? `${formData.height_cm} cm`
              : "--"
          }
        />


        <SummaryCard
          icon={
            <Weight size={20} />
          }
          label="Weight"
          value={
            formData.weight_kg
              ? `${formData.weight_kg} kg`
              : "--"
          }
        />


        <SummaryCard
          icon={
            <Activity size={20} />
          }
          label="BMI"
          value={bmi}
        />


        <SummaryCard
          icon={
            <Target size={20} />
          }
          label="Current Goal"
          value={
            formatGoal(
              formData.goal
            )
          }
        />

      </section>


      <form onSubmit={handleSubmit}>


        {/* ===================================================
            PERSONAL INFORMATION
        =================================================== */}

        <section className="form-card">

          <FormSectionHeader
            icon={
              <UserRound size={21} />
            }
            title="Personal Information"
            description="Basic information used to calculate your nutrition requirements."
          />


          <div className="form-grid">


            <FormField label="Full Name">

                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  disabled={profileExists}
                  onChange={handleChange}
                  placeholder="Enter your name"
                  required
                />

                  {profileExists && (
                  <small>
                  🔒 Set when your account was created
                  </small>
              )}
            </FormField>


            <FormField label="Age">

              <div className="input-with-unit">
                <input
                  type="number"
                  name="age"
                  min="1"
                  max="119"
                  value={formData.age}
                  disabled={profileExists}
                  onChange={handleChange}
                  required
                  />

                <span>years</span>
                </div>

                {profileExists && (
                  <small>
                    🔒 Account identity information
                  </small>
                )}
              </FormField>


            <FormField label="Gender">

              <select
                name="gender"
                value={formData.gender}
                disabled={profileExists}
                onChange={handleChange}
                required
                >
                  <option value="">
                    Select gender
                  </option>

                  <option value="male">
                    Male
                  </option>

                  <option value="female">
                    Female
                  </option>
              </select>

                {profileExists && (
                  <small>
                    🔒 Account identity information
                  </small>
                )}
              </FormField>


            <FormField label="Height">

              <div className="input-with-unit">

                <input
                  type="number"
                  name="height_cm"
                  value={
                    formData.height_cm
                  }
                  onChange={
                    handleChange
                  }
                  min="1"
                  step="0.1"
                  required
                />

                <span>
                  cm
                </span>

              </div>

            </FormField>


            <FormField label="Weight">

              <div className="input-with-unit">

                <input
                  type="number"
                  name="weight_kg"
                  value={
                    formData.weight_kg
                  }
                  onChange={
                    handleChange
                  }
                  min="1"
                  step="0.1"
                  required
                />

                <span>
                  kg
                </span>

              </div>

            </FormField>


          </div>

        </section>


        {/* ===================================================
            HEALTH INFORMATION
        =================================================== */}

        <section className="form-card">

          <FormSectionHeader
            icon={
              <HeartPulse size={21} />
            }
            title="Health Information"
            description="These details help MealMind provide more appropriate nutrition guidance."
          />


          <div className="form-grid">


            <FormField label="Blood Pressure">

              <div className="bp-inputs">

                <input
                  type="number"
                  name="systolic_bp"
                  value={
                    formData.systolic_bp
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="120"
                />

                <span>
                  /
                </span>

                <input
                  type="number"
                  name="diastolic_bp"
                  value={
                    formData.diastolic_bp
                  }
                  onChange={
                    handleChange
                  }
                  placeholder="80"
                />

                <small>
                  mmHg
                </small>

              </div>

            </FormField>


            <FormField label="Blood Sugar">

              <div className="input-with-unit">

                <input
                  type="number"
                  name="blood_sugar_mg_dl"
                  value={
                    formData.blood_sugar_mg_dl
                  }
                  onChange={
                    handleChange
                  }
                />

                <span>
                  mg/dL
                </span>

              </div>

            </FormField>


            <FormField label="Thyroid Status">

              <select
                name="thyroid_status"
                value={
                  formData.thyroid_status
                }
                onChange={
                  handleChange
                }
              >

                <option value="">
                  Select status
                </option>

                <option value="normal">
                  Normal
                </option>

                <option value="hypothyroid">
                  Hypothyroid
                </option>

                <option value="hyperthyroid">
                  Hyperthyroid
                </option>

                <option value="unknown">
                  Not Sure
                </option>

              </select>

            </FormField>


            {/* Women's Health
                Only visible when Female is selected */}

            {isFemale && (

              <FormField label="Women's Health">

                <select
                  name="women_health_condition"
                  value={
                    formData.women_health_condition ||
                    "none"
                  }
                  onChange={
                    handleChange
                  }
                >

                  <option value="none">
                    None
                  </option>

                  <option value="pcos">
                    PCOS
                  </option>

                  <option value="menstrual_wellness">
                    Menstrual Wellness
                  </option>

                  <option value="pregnancy">
                    Pregnancy
                  </option>

                  <option value="breastfeeding">
                    Breastfeeding
                  </option>

                </select>

              </FormField>

            )}


          </div>

        </section>


        {/* ===================================================
            HEALTH REPORTS
        =================================================== */}

        <section className="form-card">

          <FormSectionHeader
            icon={
              <FileText size={21} />
            }
            title="Health Reports"
            description="Upload a health report to extract useful values. Nothing updates your active profile until you review and confirm it."
          />

          {!profileExists && (
            <div className="message-box">
              Save your health profile first. Report upload becomes available after the profile is created.
            </div>
          )}

          {reportError && (
            <div className="message-box error-message">
              {reportError}
            </div>
          )}

          {reportMessage && (
            <div className="message-box success-message">
              <CheckCircle2 size={18} />
              {reportMessage}
            </div>
          )}

          <div
            style={{
              border: "1px dashed #cbd5e1",
              borderRadius: "14px",
              padding: "20px",
              marginTop: "16px",
            }}
          >
            <div
              style={{
                display: "flex",
                gap: "12px",
                alignItems: "center",
                flexWrap: "wrap",
              }}
            >
              <UploadCloud size={24} />

              <div style={{ flex: 1 }}>
                <strong>
                  Upload health report
                </strong>

                <div
                  style={{
                    fontSize: "0.9rem",
                    marginTop: "4px",
                  }}
                >
                  PDF, JPG, JPEG, PNG or WEBP · maximum 10 MB
                </div>
              </div>

              <input
                key={reportInputKey}
                type="file"
                accept=".pdf,.jpg,.jpeg,.png,.webp,application/pdf,image/jpeg,image/png,image/webp"
                onChange={handleReportFileChange}
                disabled={
                  !profileExists ||
                  analyzingReport ||
                  confirmingReport
                }
              />
            </div>

            {reportFile && (
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: "10px",
                  marginTop: "16px",
                  flexWrap: "wrap",
                }}
              >
                <FileText size={18} />

                <span style={{ flex: 1 }}>
                  {reportFile.name}
                </span>

                <button
                  type="button"
                  onClick={clearSelectedReport}
                  disabled={
                    analyzingReport ||
                    confirmingReport
                  }
                >
                  <X size={16} />
                  Remove
                </button>

                <button
                  type="button"
                  className="primary-button"
                  onClick={handleAnalyzeReport}
                  disabled={
                    analyzingReport ||
                    confirmingReport
                  }
                >
                  {analyzingReport ? (
                    <RefreshCw size={18} />
                  ) : (
                    <UploadCloud size={18} />
                  )}

                  {analyzingReport
                    ? "Analyzing..."
                    : "Analyze Report"}
                </button>
              </div>
            )}
          </div>


          {reportDraft && (
            <div
              style={{
                marginTop: "22px",
                borderTop: "1px solid #e2e8f0",
                paddingTop: "20px",
              }}
            >
              <h3>
                Review Extracted Information
              </h3>

              <p>
                AI extraction is only a pre-fill. Check the report yourself and correct any value before confirming.
              </p>

              <div className="form-grid">

                <FormField label="Report Date">
                  <input
                    type="date"
                    value={
                      reportDraft.report_date ||
                      ""
                    }
                    onChange={(event) =>
                      updateReportDraftField(
                        "report_date",
                        event.target.value
                      )
                    }
                  />
                </FormField>

                <FormField label="Systolic BP">
                  <input
                    type="number"
                    value={
                      reportDraft.systolic_bp
                    }
                    onChange={(event) =>
                      updateReportDraftField(
                        "systolic_bp",
                        event.target.value
                      )
                    }
                    placeholder="Not found"
                  />

                  <ReportComparison
                    currentValue={
                      reportPreview?.current_profile
                        ?.systolic_bp
                    }
                    newValue={
                      reportDraft.systolic_bp
                    }
                    unit="mmHg"
                  />
                </FormField>

                <FormField label="Diastolic BP">
                  <input
                    type="number"
                    value={
                      reportDraft.diastolic_bp
                    }
                    onChange={(event) =>
                      updateReportDraftField(
                        "diastolic_bp",
                        event.target.value
                      )
                    }
                    placeholder="Not found"
                  />

                  <ReportComparison
                    currentValue={
                      reportPreview?.current_profile
                        ?.diastolic_bp
                    }
                    newValue={
                      reportDraft.diastolic_bp
                    }
                    unit="mmHg"
                  />
                </FormField>

                <FormField label="Blood Sugar">
                  <div className="input-with-unit">
                    <input
                      type="number"
                      value={
                        reportDraft.blood_sugar_mg_dl
                      }
                      onChange={(event) =>
                        updateReportDraftField(
                          "blood_sugar_mg_dl",
                          event.target.value
                        )
                      }
                      placeholder="Not found"
                    />

                    <span>
                      mg/dL
                    </span>
                  </div>

                  <ReportComparison
                    currentValue={
                      reportPreview?.current_profile
                        ?.blood_sugar_mg_dl
                    }
                    newValue={
                      reportDraft.blood_sugar_mg_dl
                    }
                    unit="mg/dL"
                  />
                </FormField>

                <FormField label="Thyroid Status">
                  <input
                    type="text"
                    value={
                      reportDraft.thyroid_status
                    }
                    onChange={(event) =>
                      updateReportDraftField(
                        "thyroid_status",
                        event.target.value
                      )
                    }
                    placeholder="Not found"
                  />

                  <ReportComparison
                    currentValue={
                      reportPreview?.current_profile
                        ?.thyroid_status
                    }
                    newValue={
                      reportDraft.thyroid_status
                    }
                  />
                </FormField>

              </div>


              <div
                style={{
                  marginTop: "22px",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center",
                    gap: "12px",
                    flexWrap: "wrap",
                  }}
                >
                  <div>
                    <h3>
                      Additional Health Information
                    </h3>

                    <p>
                      Other useful measured results found in the report.
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={addAdditionalHealthItem}
                  >
                    + Add Result
                  </button>
                </div>

                {reportDraft.additional_health_info
                  .length === 0 && (
                  <p>
                    No additional measured health values were extracted.
                  </p>
                )}

                {reportDraft.additional_health_info.map(
                  (item, index) => (
                    <div
                      key={`${index}-${item.name}`}
                      style={{
                        display: "grid",
                        gridTemplateColumns:
                          "minmax(150px, 2fr) minmax(100px, 1fr) minmax(100px, 1fr) minmax(100px, 1fr) auto",
                        gap: "10px",
                        marginTop: "12px",
                        alignItems: "center",
                      }}
                    >
                      <input
                        type="text"
                        value={item.name}
                        placeholder="Test name"
                        onChange={(event) =>
                          updateAdditionalHealthItem(
                            index,
                            "name",
                            event.target.value
                          )
                        }
                      />

                      <input
                        type="text"
                        value={item.value}
                        placeholder="Value"
                        onChange={(event) =>
                          updateAdditionalHealthItem(
                            index,
                            "value",
                            event.target.value
                          )
                        }
                      />

                      <input
                        type="text"
                        value={item.unit}
                        placeholder="Unit"
                        onChange={(event) =>
                          updateAdditionalHealthItem(
                            index,
                            "unit",
                            event.target.value
                          )
                        }
                      />

                      <input
                        type="text"
                        value={item.report_flag}
                        placeholder="Flag"
                        onChange={(event) =>
                          updateAdditionalHealthItem(
                            index,
                            "report_flag",
                            event.target.value
                          )
                        }
                      />

                      <button
                        type="button"
                        title="Remove extracted result"
                        onClick={() =>
                          removeAdditionalHealthItem(
                            index
                          )
                        }
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  )
                )}
              </div>


              <div
                className="form-actions"
                style={{
                  marginTop: "22px",
                }}
              >
                <div>
                  <strong>
                    Confirm only after checking the report.
                  </strong>

                  <span>
                    Missing fields will not erase existing profile values. Confirmed newer values become the active values.
                  </span>
                </div>

                <button
                  type="button"
                  className="primary-button"
                  onClick={handleConfirmReport}
                  disabled={confirmingReport}
                >
                  <CheckCircle2 size={18} />

                  {confirmingReport
                    ? "Confirming..."
                    : "Confirm & Update Profile"}
                </button>
              </div>

            </div>
          )}


          {profileExists && (
            <div
              style={{
                marginTop: "26px",
                borderTop: "1px solid #e2e8f0",
                paddingTop: "20px",
              }}
            >
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                  gap: "12px",
                  flexWrap: "wrap",
                }}
              >
                <div>
                  <h3>
                    Report History
                  </h3>

                  <p>
                    Only structured extracted history is retained in this V1 flow.
                  </p>
                </div>

                <strong>
                  {reportHistory.length} / 10 uploaded
                </strong>
              </div>

              {reportHistoryLoading ? (
                <p>
                  Loading report history...
                </p>
              ) : reportHistory.length === 0 ? (
                <p>
                  No confirmed health reports yet.
                </p>
              ) : (
                <div
                  style={{
                    display: "grid",
                    gap: "10px",
                    marginTop: "14px",
                  }}
                >
                  {reportHistory.map((report) => (
                    <div
                      key={report.id}
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: "12px",
                        padding: "12px",
                        border: "1px solid #e2e8f0",
                        borderRadius: "12px",
                      }}
                    >
                      <FileText size={19} />

                      <div style={{ flex: 1 }}>
                        <strong>
                          {report.original_filename ||
                            "Health Report"}
                        </strong>

                        <div
                          style={{
                            fontSize: "0.85rem",
                            marginTop: "3px",
                          }}
                        >
                          {formatReportDate(
                            report.report_date ||
                              report.created_at
                          )}
                        </div>
                      </div>

                      <button
                        type="button"
                        title="Delete report history"
                        onClick={() =>
                          handleDeleteReport(
                            report.id
                          )
                        }
                        disabled={
                          deletingReportId ===
                          report.id
                        }
                      >
                        <Trash2 size={17} />

                        {deletingReportId ===
                        report.id
                          ? "Deleting..."
                          : "Delete"}
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

        </section>


        {/* ===================================================
            LIFESTYLE & GOAL
        =================================================== */}

        <section className="form-card">

          <FormSectionHeader
            icon={
              <Activity size={21} />
            }
            title="Lifestyle & Goal"
            description="Tell us about your lifestyle, food region and what you want to achieve."
          />


          <div className="form-grid">


            <FormField label="Activity Level">

              <select
                name="activity_level"
                value={
                  formData.activity_level
                }
                onChange={
                  handleChange
                }
                required
              >

                <option value="">
                  Select activity level
                </option>

                <option value="sedentary">
                  Sedentary
                </option>

                <option value="light">
                  Lightly Active
                </option>

                <option value="moderate">
                  Moderately Active
                </option>

                <option value="active">
                  Active
                </option>

                <option value="very_active">
                  Very Active
                </option>

              </select>

            </FormField>


            <FormField label="Diet Preference">

              <select
                name="diet_preference"
                value={
                  formData.diet_preference
                }
                onChange={
                  handleChange
                }
              >

                <option value="">
                  Select preference
                </option>

                <option value="vegetarian">
                  Vegetarian
                </option>

                <option value="non-vegetarian">
                  Non-Vegetarian
                </option>

                <option value="vegan">
                  Vegan
                </option>

                <option value="eggetarian">
                  Eggetarian
                </option>

              </select>

            </FormField>


            <FormField label="State / Food Region">

              <select
                name="food_region"
                value={
                  formData.food_region
                }
                onChange={
                  handleChange
                }
              >

                <option value="">
                  Select your state / food region
                </option>

                <option value="Andhra Pradesh">
                  Andhra Pradesh
                </option>

                <option value="Arunachal Pradesh">
                  Arunachal Pradesh
                </option>

                <option value="Assam">
                  Assam
                </option>

                <option value="Bihar">
                  Bihar
                </option>

                <option value="Chhattisgarh">
                  Chhattisgarh
                </option>

                <option value="Goa">
                  Goa
                </option>

                <option value="Gujarat">
                  Gujarat
                </option>

                <option value="Haryana">
                  Haryana
                </option>

                <option value="Himachal Pradesh">
                  Himachal Pradesh
                </option>

                <option value="Jharkhand">
                  Jharkhand
                </option>

                <option value="Karnataka">
                  Karnataka
                </option>

                <option value="Kerala">
                  Kerala
                </option>

                <option value="Madhya Pradesh">
                  Madhya Pradesh
                </option>

                <option value="Maharashtra">
                  Maharashtra
                </option>

                <option value="Manipur">
                  Manipur
                </option>

                <option value="Meghalaya">
                  Meghalaya
                </option>

                <option value="Mizoram">
                  Mizoram
                </option>

                <option value="Nagaland">
                  Nagaland
                </option>

                <option value="Odisha">
                  Odisha
                </option>

                <option value="Punjab">
                  Punjab
                </option>

                <option value="Rajasthan">
                  Rajasthan
                </option>

                <option value="Sikkim">
                  Sikkim
                </option>

                <option value="Tamil Nadu">
                  Tamil Nadu
                </option>

                <option value="Telangana">
                  Telangana
                </option>

                <option value="Tripura">
                  Tripura
                </option>

                <option value="Uttar Pradesh">
                  Uttar Pradesh
                </option>

                <option value="Uttarakhand">
                  Uttarakhand
                </option>

                <option value="West Bengal">
                  West Bengal
                </option>

                <option value="Andaman and Nicobar Islands">
                  Andaman and Nicobar Islands
                </option>

                <option value="Chandigarh">
                  Chandigarh
                </option>

                <option value="Dadra and Nagar Haveli and Daman and Diu">
                  Dadra and Nagar Haveli and Daman and Diu
                </option>

                <option value="Delhi">
                  Delhi
                </option>

                <option value="Jammu and Kashmir">
                  Jammu and Kashmir
                </option>

                <option value="Ladakh">
                  Ladakh
                </option>

                <option value="Lakshadweep">
                  Lakshadweep
                </option>

                <option value="Puducherry">
                  Puducherry
                </option>

              </select>

            </FormField>


            <FormField label="Your Goal">

              <select
                name="goal"
                value={
                  formData.goal
                }
                onChange={
                  handleChange
                }
                required
              >

                <option value="">
                  Select your goal
                </option>

                <option value="weight_loss">
                  Weight Loss
                </option>

                <option value="maintenance">
                  Maintain Weight
                </option>

                <option value="weight_gain">
                  Weight Gain
                </option>

                <option value="muscle_gain">
                  Muscle Gain
                </option>

                <option value="strength_gain">
                  Strength Gain
                </option>

              </select>

            </FormField>


          </div>

        </section>


        {/* ===================================================
            SAVE
        =================================================== */}

        <div className="form-actions">

          <div>

            <strong>
              Your information stays in your profile.
            </strong>

            <span>
              MealMind uses these details when
              creating personalized nutrition guidance.
            </span>

          </div>


          <button
            type="submit"
            className="primary-button"
            disabled={saving}
          >

            <Save size={18} />

            {saving
              ? "Saving..."
              : profileExists
                ? "Update Health Profile"
                : "Complete Health Profile"}

          </button>

        </div>


      </form>

    </div>
  );
}


// ===========================================================
// FORM SECTION HEADER
// ===========================================================

function FormSectionHeader({
  icon,
  title,
  description,
}) {
  return (
    <div className="form-section-header">

      <div className="form-section-icon">
        {icon}
      </div>

      <div>

        <h2>
          {title}
        </h2>

        <p>
          {description}
        </p>

      </div>

    </div>
  );
}


// ===========================================================
// FORM FIELD
// ===========================================================

function FormField({
  label,
  children,
}) {
  return (
    <label className="form-field">

      <span>
        {label}
      </span>

      {children}

    </label>
  );
}


// ===========================================================
// SUMMARY CARD
// ===========================================================

function SummaryCard({
  icon,
  label,
  value,
}) {
  return (
    <div className="health-summary-card">

      <div className="health-summary-icon">
        {icon}
      </div>

      <div>

        <span>
          {label}
        </span>

        <strong>
          {value}
        </strong>

      </div>

    </div>
  );
}


// ===========================================================
// REPORT VALUE COMPARISON
// ===========================================================

function ReportComparison({
  currentValue,
  newValue,
  unit = "",
}) {
  const hasCurrent =
    currentValue !== null &&
    currentValue !== undefined &&
    currentValue !== "";

  const hasNew =
    newValue !== null &&
    newValue !== undefined &&
    newValue !== "";

  if (!hasNew) {
    return (
      <small>
        Not found in this report. Existing value will remain unchanged.
      </small>
    );
  }

  const changed =
    String(currentValue ?? "") !==
    String(newValue ?? "");

  return (
    <small>
      {hasCurrent
        ? `Current: ${currentValue}${unit ? ` ${unit}` : ""}`
        : "Current: not set"}

      {" → "}

      {changed
        ? `New: ${newValue}${unit ? ` ${unit}` : ""}`
        : "No change"}
    </small>
  );
}


// ===========================================================
// FORMAT REPORT DATE
// ===========================================================

function formatReportDate(value) {
  if (!value) {
    return "Date not available";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return String(value);
  }

  return date.toLocaleDateString();
}


// ===========================================================
// FORMAT GOAL
// ===========================================================

function formatGoal(goal) {
  const goals = {
    weight_loss:
      "Weight Loss",

    maintenance:
      "Maintain",

    weight_gain:
      "Weight Gain",

    muscle_gain:
      "Muscle Gain",

    strength_gain:
      "Strength Gain",
  };


  return (
    goals[goal] ||
    "Not Set"
  );
}


export default HealthProfile;